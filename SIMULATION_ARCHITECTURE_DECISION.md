# Simulation Platform Architecture Decision

## **Decision: API-Based Integration (Recommended)**

After analyzing the requirements, we've decided to keep the simulation platform **completely separate** and use **API-based integration** between the main backend and simulation platform.

## **Architecture Overview**

```
┌─────────────────────┐    HTTP API Calls    ┌─────────────────────┐
│   Main Backend      │ ──────────────────► │ Simulation Platform │
│   (Port 8000)       │                     │   (Port 8001)       │
│                     │                     │                     │
│ - User Auth         │                     │ - Challenge Mgmt    │
│ - Main Platform     │                     │ - Container Spawn   │
│ - Gateway/Proxy     │                     │ - Manual Triage     │
│ - Integration       │                     │ - Scoring System    │
└─────────────────────┘                     └─────────────────────┘
         │                                           │
         ▼                                           ▼
┌─────────────────────┐                     ┌─────────────────────┐
│ Production Database │                     │ Simulation Database │
│   (Port 5432)       │                     │   (Port 5433)       │
└─────────────────────┘                     └─────────────────────┘
```

## **Implementation Strategy**

### **1. Backend Acts as Gateway**
- **File**: `backend/src/api/v1/endpoints/simulation_gateway.py`
- **Purpose**: Proxy requests to simulation platform
- **Responsibilities**:
  - User authentication (main platform)
  - Request forwarding to simulation API
  - Response handling and integration
  - Error handling and fallbacks

### **2. API Client Service**
- **File**: `backend/src/services/simulation_api_client.py`
- **Purpose**: HTTP client for simulation platform
- **Features**:
  - Async HTTP requests
  - Error handling and retries
  - Connection pooling
  - Health checks

### **3. Simulation Platform (Isolated)**
- **Location**: `simulation/` directory
- **Port**: 8001
- **Database**: Separate PostgreSQL (port 5433)
- **Responsibilities**:
  - Challenge management
  - Container orchestration
  - Manual triage workflow
  - Scoring and feedback
  - Isolated user sessions

## **Workflow Integration**

### **User Journey**:
1. **Login**: User logs into main platform (backend:8000)
2. **Navigate**: Frontend redirects to simulation panel
3. **Gateway**: Backend forwards requests to simulation platform (8001)
4. **Isolation**: Simulation platform handles everything independently
5. **Results**: Results flow back through gateway to main platform

### **API Flow Example**:
```
Frontend → Backend Gateway → Simulation Platform
   ↓              ↓                    ↓
Main DB    ←─ Integration ─→    Simulation DB
```

## **Benefits of This Architecture**

### **✅ Advantages**:
1. **True Isolation**: Complete separation of production and simulation data
2. **Independent Scaling**: Each service scales independently
3. **Security**: Clear security boundaries
4. **Maintainability**: Easier to maintain and update
5. **Testing**: Can test simulation platform independently
6. **Deployment**: Can deploy services separately
7. **Technology Freedom**: Each service can use different tech stacks

### **⚠️ Considerations**:
1. **Network Latency**: Additional HTTP calls
2. **Complexity**: More moving parts
3. **Error Handling**: Need robust error handling
4. **Monitoring**: Need to monitor both services

## **File Organization**

### **Keep Separate**:
- `backend/` - Main platform code
- `simulation/` - Simulation platform code
- Different databases, containers, ports

### **Integration Points**:
- `backend/src/services/simulation_api_client.py` - HTTP client
- `backend/src/api/v1/endpoints/simulation_gateway.py` - Gateway endpoints

## **Migration Strategy**

### **Phase 1: API Client Setup** ✅
- Created `simulation_api_client.py`
- Created `simulation_gateway.py`
- Set up HTTP communication

### **Phase 2: Replace Direct Calls**
- Update existing `simulation.py` to use gateway
- Remove direct database calls from backend
- Update tests to use API mocking

### **Phase 3: Complete Isolation**
- Remove simulation models from backend
- Remove simulation services from backend
- Update frontend to use gateway endpoints

## **Current Status**

### **✅ Completed**:
- Simulation platform running on port 8001
- Separate databases (5432 vs 5433)
- API client service created
- Gateway endpoints created

### **🔧 Next Steps**:
1. Start simulation platform successfully
2. Test API communication
3. Update existing backend endpoints
4. Update frontend integration
5. Remove duplicate simulation code from backend

## **Recommendation**

**Use the API-based integration approach** because:
- Maintains true isolation as discussed
- Follows microservices best practices
- Easier to scale and maintain
- Clearer separation of concerns
- Better security boundaries

The simulation platform should remain completely independent, with the backend acting only as an authenticated gateway.