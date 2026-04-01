import { create } from 'zustand';
import api from '@/lib/api';
import { normalizeUser, type UserProfile } from '@/lib/portal';

interface AuthState {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string, mfaCode?: string) => Promise<UserProfile>;
  register: (data: RegisterData) => Promise<any>;
  logout: () => void;
  checkAuth: () => Promise<void>;
  enableMFA: () => Promise<{ secret: string; qr_uri: string; backup_codes: string[]; message: string }>;
  verifyMFASetup: (code: string) => Promise<void>;
  disableMFA: (password: string) => Promise<void>;
  verifyEmail: (token: string) => Promise<void>;
  resendVerification: (email: string) => Promise<void>;
}

interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  role: 'researcher' | 'organization';
  country?: string;
  organization_name?: string;
  phone_number?: string;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  login: async (email: string, password: string, mfaCode?: string) => {
    try {
      const requestData = {
        email: email,
        password: password,
        mfa_code: mfaCode
      };

      const response = await api.post('/auth/login', requestData, {
        headers: { 'Content-Type': 'application/json' },
      });

      const data = response.data;

      // Check if MFA is required (backend returns mfa_required: true)
      if (data.mfa_required) {
        set({ isLoading: false });
        throw { mfaRequired: true, userId: data.user_id };
      }
      
      localStorage.setItem('access_token', data.access_token);
      if (data.refresh_token) {
        localStorage.setItem('refresh_token', data.refresh_token);
      }

      let user = normalizeUser({
        id: data.user_id,
        email: data.email,
        role: data.role,
        mfa_enabled: data.mfa_enabled,
        is_verified: true,
      });

      try {
        const profileResponse = await api.get('/users/me');
        user = normalizeUser({
          ...profileResponse.data,
          role: data.role,
          mfa_enabled: data.mfa_enabled ?? profileResponse.data?.mfa_enabled,
          is_verified:
            profileResponse.data?.email_verified ??
            profileResponse.data?.is_verified ??
            true,
        });
      } catch {
        // Fall back to token response if profile hydration fails.
      }

      set({ user, isAuthenticated: true, isLoading: false });
      return user;
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  register: async (data: RegisterData) => {
    try {
      // Determine the correct endpoint based on role
      const endpoint = data.role === 'researcher' 
        ? '/registration/researcher/initiate' 
        : '/registration/organization/initiate';
      
      // Prepare the request data based on role
      const requestData = data.role === 'researcher' 
        ? {
            email: data.email,
            password: data.password,
            first_name: data.first_name,
            last_name: data.last_name
          }
        : {
            email: data.email,
            password: data.password,
            first_name: data.first_name,
            last_name: data.last_name,
            company_name: data.organization_name,
            phone_number: data.phone_number,
            country: data.country
          };
      
      const response = await api.post(endpoint, requestData);
      
      // Registration initiated - user needs to verify OTP
      set({ isLoading: false });
      
      return response.data; // Return registration response for UI feedback
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({ user: null, isAuthenticated: false });
  },

  checkAuth: async () => {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      set({ isLoading: false, isAuthenticated: false });
      return;
    }

    try {
      const response = await api.get('/users/me');
      set((state) => ({
        user: normalizeUser({
          ...response.data,
          mfa_enabled: response.data?.mfa_enabled ?? state.user?.mfaEnabled,
          is_verified:
            response.data?.email_verified ??
            response.data?.is_verified ??
            state.user?.emailVerified ??
            true,
        }),
        isAuthenticated: true,
        isLoading: false,
      }));
    } catch (error) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  enableMFA: async () => {
    try {
      const response = await api.post('/auth/mfa/enable');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  verifyMFASetup: async (code: string) => {
    try {
      const response = await api.post('/auth/mfa/verify', { code });
      
      // Update user state to reflect MFA is now enabled
      set((state) => ({
        user: state.user ? { ...state.user, mfaEnabled: true } : null
      }));
      
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  disableMFA: async (password: string) => {
    try {
      const response = await api.post('/auth/mfa/disable', { password });
      
      // Update user state to reflect MFA is now disabled
      set((state) => ({
        user: state.user ? { ...state.user, mfaEnabled: false } : null
      }));
      
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  verifyEmail: async (token: string) => {
    try {
      const response = await api.post('/auth/verify-email', { token });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  resendVerification: async (email: string) => {
    try {
      const response = await api.post('/auth/resend-verification', { email });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
}));
