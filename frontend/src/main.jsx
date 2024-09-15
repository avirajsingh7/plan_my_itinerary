import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Route, BrowserRouter as Router, Routes } from "react-router-dom";
import PrivateRoutes from "./components/PrivateRoutes.jsx";
import { AuthProvider } from "./contexts/AuthContext.jsx";
import ItineraryProvider from "./contexts/ItineraryContext.jsx";
import "./index.css";
import { LandingPage, LoginPage, SignupPage, TimelinePage } from "./pages";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <AuthProvider>
      <ItineraryProvider>
        <Router>
          <Routes>
            <Route element={<PrivateRoutes />}>
              <Route path="/" element={<LandingPage />} />
              <Route path="timeline" element={<TimelinePage />} />
            </Route>
            <Route path="login" element={<LoginPage />} />
            <Route path="signup" element={<SignupPage />} />
          </Routes>
        </Router>
      </ItineraryProvider>
    </AuthProvider>
  </StrictMode>
);
