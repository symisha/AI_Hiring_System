// src/components/ProtectedRoute.tsx
import { Navigate } from "react-router-dom";

export const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
  const token = localStorage.getItem("token");
  if (!token) {
    return <Navigate to="/hr-login" replace />;
  }
  return children;
};

export default ProtectedRoute;