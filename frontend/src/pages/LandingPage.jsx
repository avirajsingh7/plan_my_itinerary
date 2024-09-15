import Cookies from "js-cookie";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Recents from "../components/Recents";
import SearchBar from "../components/SearchBar";
import { useAuth } from "../contexts/AuthContext";
import user from "../services/authentication";

export default function LandingPage() {
  const navigate = useNavigate();
  const { setAuthUser, setIsLoggedin } = useAuth();

  useEffect(() => {
    const token = Cookies.get("access_token");
    if (!token) navigate("/login");

    user.getDetails(token).then((res) => {
      setAuthUser(res.first_name);
      setIsLoggedin(true);
    });
  }, []);

  return (
    <div className="w-full h-[80dvh] text-teal-700">
      <section className="p-6 text-center shadow-lg shadow-teal-100 z-20 border-2 border-teal-400 rounded-b-full">
        <h1 className="text-4xl text-teal-500 drop-shadow-2xl text-center font-900 pt-5">
          Your Journey, Perfected By AI
        </h1>
      </section>
      <SearchBar />
      <Recents />
    </div>
  );
}
