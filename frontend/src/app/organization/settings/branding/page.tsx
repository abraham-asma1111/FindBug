'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useToast } from '@/components/ui/Toast';
import { api } from '@/lib/api';

export default function OrganizationBrandingPage() {
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  const { showToast } = useToast();
  const [brandColor, setBrandColor] = useState('#3B82F6');
  const [logoFile, setLogoFile] = useState<File | null>(null);
  const [coverFile, setCoverFile] = useState<File | null>(null);
  const [logoPreview, setLogoPreview] = useState<string | null>(null);
  const [coverPreview, setCoverPreview] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  // Fetch current branding
  const { data: branding, isLoading, refetch } = useApiQuery<any>({
    endpoint: '/organization/branding',
  });

  // Set initial brand color from API
  useEffect(() => {
    if (branding?.brand_color) {
      setBrandColor(branding.brand_color);
    }
  }, [branding]);

  const handleLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setLogoFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setLogoPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleCoverChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setCoverFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setCoverPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUploadLogo = async () => {
    if (!logoFile) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', logoFile);

    try {
      await api.post('/organization/branding/upload-logo', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      showToast('Logo uploaded successfully', 'success');
      setLogoFile(null);
      setLogoPreview(null);
      refetch();
    } catch (error: any) {
      showToast(error.response?.data?.detail || 'Failed to upload logo', 'error');
    } finally {
      setIsUploading(false);
    }
  };

  const handleUploadCover = async () => {
    if (!coverFile) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', coverFile);

    try {
      await api.post('/organization/branding/upload-cover', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      showToast('Cover image uploaded successfully', 'success');
      setCoverFile(null);
      setCoverPreview(null);
      refetch();
    } catch (error: any) {
      showToast(error.response?.data?.detail || 'Failed to upload cover image', 'error');
    } finally {
      setIsUploading(false);
    }
  };

  const handleSaveSettings = async () => {
    try {
      await api.put('/organization/branding/settings', {
        brand_color: brandColor,
      });
      showToast('Branding settings updated successfully', 'success');
      refetch();
    } catch (error: any) {
      showToast(error.response?.data?.detail || 'Failed to update branding settings', 'error');
    }
  };

  const handleDeleteLogo = async () => {
    try {
      await api.delete('/organization/branding/logo');
      showToast('Logo removed successfully', 'success');
      refetch();
    } catch (error: any) {
      showToast(error.response?.data?.detail || 'Failed to remove logo', 'error');
    }
  };

  const handleDeleteCover = async () => {
    try {
      await api.delete('/organization/branding/cover');
      showToast('Cover image removed successfully', 'success');
      refetch();
    } catch (error: any) {
      showToast(error.response?.data?.detail || 'Failed to remove cover image', 'error');
    }
  };

  if (!user) return null;

  return (
    <ProtectedRoute allowedRoles={['organization']}>
      <PortalShell
        user={user}
        title="Branding Settings"
        subtitle="Customize your organization's appearance"
        navItems={getPortalNavItems(user.role)}
        hideThemeToggle={true}
      >
        {/* Back Button */}
        <div className="mb-6">
          <button
            onClick={() => router.push('/organization/dashboard')}
            className="flex items-center gap-2 text-[#94A3B8] hover:text-[#F8FAFC] transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Dashboard
          </button>
        </div>

        {isLoading ? (
          <div className="bg-[#1E293B] rounded-lg border border-[#334155] p-12 text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-[#334155] border-t-[#3B82F6] mb-4"></div>
            <p className="text-[#94A3B8]">Loading branding settings...</p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Logo Upload Section */}
            <div className="bg-[#1E293B] rounded-xl border border-[#334155] p-8">
              <h2 className="text-2xl font-bold text-[#F8FAFC] mb-6 flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-[#3B82F6]/10 flex items-center justify-center">
                  <svg className="w-5 h-5 text-[#3B82F6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                Organization Logo
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Current Logo */}
                <div>
                  <p className="text-[#94A3B8] text-sm font-medium mb-3">Current Logo</p>
                  <div className="bg-[#0F172A] rounded-lg border border-[#334155] p-6 flex items-center justify-center h-48">
                    {branding?.logo_url ? (
                      <img
                        src={`/api/v1/files/serve/${branding.logo_url}`}
                        alt="Organization Logo"
                        className="max-h-full max-w-full object-contain"
                      />
                    ) : (
                      <div className="text-center">
                        <svg className="w-16 h-16 text-[#475569] mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        <p className="text-[#64748B] text-sm">No logo uploaded</p>
                      </div>
                    )}
                  </div>
                  {branding?.logo_url && (
                    <button
                      onClick={handleDeleteLogo}
                      className="mt-3 w-full px-4 py-2 bg-[#EF4444]/10 text-[#EF4444] rounded-lg hover:bg-[#EF4444]/20 transition-colors border border-[#EF4444]/30 font-medium"
                    >
                      Remove Logo
                    </button>
                  )}
                </div>

                {/* Upload New Logo */}
                <div>
                  <p className="text-[#94A3B8] text-sm font-medium mb-3">Upload New Logo</p>
                  <div className="bg-[#0F172A] rounded-lg border border-[#334155] p-6 flex items-center justify-center h-48">
                    {logoPreview ? (
                      <img
                        src={logoPreview}
                        alt="Logo Preview"
                        className="max-h-full max-w-full object-contain"
                      />
                    ) : (
                      <label className="cursor-pointer text-center">
                        <input
                          type="file"
                          accept="image/*"
                          onChange={handleLogoChange}
                          className="hidden"
                        />
                        <svg className="w-16 h-16 text-[#475569] mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                        <p className="text-[#3B82F6] font-medium">Click to upload</p>
                        <p className="text-[#64748B] text-xs mt-1">PNG, JPG, GIF, SVG (max 5MB)</p>
                      </label>
                    )}
                  </div>
                  {logoFile && (
                    <button
                      onClick={handleUploadLogo}
                      disabled={isUploading}
                      className="mt-3 w-full px-4 py-2 bg-[#3B82F6] text-white rounded-lg hover:bg-[#2563EB] transition-colors font-medium disabled:opacity-50"
                    >
                      {isUploading ? 'Uploading...' : 'Upload Logo'}
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Cover Image Upload Section */}
            <div className="bg-[#1E293B] rounded-xl border border-[#334155] p-8">
              <h2 className="text-2xl font-bold text-[#F8FAFC] mb-6 flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-[#8B5CF6]/10 flex items-center justify-center">
                  <svg className="w-5 h-5 text-[#8B5CF6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                Cover Image
              </h2>

              <div className="space-y-6">
                {/* Current Cover */}
                <div>
                  <p className="text-[#94A3B8] text-sm font-medium mb-3">Current Cover Image</p>
                  <div className="bg-[#0F172A] rounded-lg border border-[#334155] overflow-hidden h-64">
                    {branding?.cover_image_url ? (
                      <img
                        src={`/api/v1/files/serve/${branding.cover_image_url}`}
                        alt="Cover Image"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="flex items-center justify-center h-full">
                        <div className="text-center">
                          <svg className="w-16 h-16 text-[#475569] mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                          <p className="text-[#64748B] text-sm">No cover image uploaded</p>
                        </div>
                      </div>
                    )}
                  </div>
                  {branding?.cover_image_url && (
                    <button
                      onClick={handleDeleteCover}
                      className="mt-3 px-4 py-2 bg-[#EF4444]/10 text-[#EF4444] rounded-lg hover:bg-[#EF4444]/20 transition-colors border border-[#EF4444]/30 font-medium"
                    >
                      Remove Cover Image
                    </button>
                  )}
                </div>

                {/* Upload New Cover */}
                <div>
                  <p className="text-[#94A3B8] text-sm font-medium mb-3">Upload New Cover Image</p>
                  <div className="bg-[#0F172A] rounded-lg border border-[#334155] overflow-hidden h-64">
                    {coverPreview ? (
                      <img
                        src={coverPreview}
                        alt="Cover Preview"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <label className="cursor-pointer flex items-center justify-center h-full">
                        <input
                          type="file"
                          accept="image/*"
                          onChange={handleCoverChange}
                          className="hidden"
                        />
                        <div className="text-center">
                          <svg className="w-16 h-16 text-[#475569] mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                          </svg>
                          <p className="text-[#3B82F6] font-medium">Click to upload</p>
                          <p className="text-[#64748B] text-xs mt-1">PNG, JPG, GIF (max 10MB)</p>
                        </div>
                      </label>
                    )}
                  </div>
                  {coverFile && (
                    <button
                      onClick={handleUploadCover}
                      disabled={isUploading}
                      className="mt-3 px-4 py-2 bg-[#3B82F6] text-white rounded-lg hover:bg-[#2563EB] transition-colors font-medium disabled:opacity-50"
                    >
                      {isUploading ? 'Uploading...' : 'Upload Cover Image'}
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Brand Color Section */}
            <div className="bg-[#1E293B] rounded-xl border border-[#334155] p-8">
              <h2 className="text-2xl font-bold text-[#F8FAFC] mb-6 flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-[#F59E0B]/10 flex items-center justify-center">
                  <svg className="w-5 h-5 text-[#F59E0B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                  </svg>
                </div>
                Brand Color
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-[#94A3B8] text-sm font-medium mb-3">
                    Primary Brand Color
                  </label>
                  <div className="flex items-center gap-4">
                    <input
                      type="color"
                      value={brandColor}
                      onChange={(e) => setBrandColor(e.target.value)}
                      className="w-20 h-20 rounded-lg border-2 border-[#334155] cursor-pointer"
                    />
                    <div>
                      <input
                        type="text"
                        value={brandColor}
                        onChange={(e) => setBrandColor(e.target.value)}
                        className="bg-[#0F172A] border border-[#334155] rounded-lg px-4 py-2 text-[#F8FAFC] font-mono"
                        placeholder="#3B82F6"
                      />
                      <p className="text-[#64748B] text-xs mt-2">Hex color code</p>
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-[#94A3B8] text-sm font-medium mb-3">
                    Preview
                  </label>
                  <div 
                    className="h-20 rounded-lg border-2 border-[#334155] flex items-center justify-center"
                    style={{ backgroundColor: brandColor }}
                  >
                    <span className="text-white font-bold text-lg drop-shadow-lg">
                      Your Brand Color
                    </span>
                  </div>
                </div>
              </div>

              <button
                onClick={handleSaveSettings}
                className="mt-6 px-6 py-3 bg-[#10B981] text-white rounded-lg hover:bg-[#059669] transition-colors font-medium"
              >
                Save Brand Color
              </button>
            </div>
          </div>
        )}
      </PortalShell>
    </ProtectedRoute>
  );
}
