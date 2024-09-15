import Cookies from "js-cookie";
import { Navigate, Outlet } from "react-router-dom";

export default function PrivateRoutes() {
  const token = Cookies.get("access_token");
  return token ? <Outlet /> : <Navigate to="/login" />;
}
