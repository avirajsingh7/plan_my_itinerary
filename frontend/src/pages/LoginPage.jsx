import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import user from "../services/authentication";

const style =
  "bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5";

export default function LoginPage() {
  const { setAuthUser, setIsLoggedin } = useAuth();
  const navigate = useNavigate();

  const submitData = (e) => {
    user
      .LoginUser(e)
      .then(() => {
        user.getDetails().then((res) => {
          setAuthUser(res.first_name);
        });
      })
      .then((res) => {
        setIsLoggedin(true);
      })
      .then(() => {
        navigate("/");
      });
  };
  return (
    <section className="bg-gray-50">
      <div className="flex flex-col items-center justify-center px-6 py-8 mx-auto md:h-screen lg:py-0">
        <div className="w-full max-w-96 bg-white rounded-lg shadow">
          <div className="p-6 space-y-4 md:space-y-6 sm:p-8">
            <h1 className="text-xl font-bold leading-tight tracking-tight text-gray-900 md:text-2xl">
              Sign in to your account
            </h1>
            <form
              className="space-y-4 md:space-y-6"
              onSubmit={(e) => submitData(e)}>
              <div>
                <label
                  htmlFor="username"
                  className="block mb-2 text-sm font-medium text-gray-900">
                  Your email
                </label>
                <input
                  type="email"
                  name="username"
                  id="username"
                  className={style}
                  placeholder="name@company.com"
                  required
                />
              </div>
              <div>
                <label
                  htmlFor="password"
                  className="block mb-2 text-sm font-medium text-gray-900">
                  Password
                </label>
                <input
                  type="password"
                  name="password"
                  id="password"
                  placeholder="••••••••"
                  className={style}
                  required
                />
              </div>
              <button
                type="submit"
                className="block w-full hover:bg-teal-500 hover:text-white rounded-full py-2 bg-teal-100 ">
                Sign in
              </button>
              <p className="text-sm font-light text-gray-500">
                Don&apos;t have an account yet?{" "}
                <Link
                  to="/signup"
                  className="font-medium text-slate-600 hover:underline">
                  Sign up
                </Link>
              </p>
            </form>
          </div>
        </div>
      </div>
    </section>
  );
}
