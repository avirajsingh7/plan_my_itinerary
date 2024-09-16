import Cookies from "js-cookie";
import { conf } from "../conf";

export const formData = (event) => {
  event.preventDefault();
  const formData = new FormData(event.currentTarget);
  return Object.fromEntries(formData);
};

class User {
  async LoginUser(event) {
    const data = formData(event);

    const resp = await fetch(conf.apiUrl + "/auth/token/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!resp.ok) throw new Error({ message: "check your credentials" });

    const respData = await resp.json();

    Cookies.set("access_token", respData.access, {
      expires: 7,
      secure: true,
      sameSite: "Strict",
    });

    return respData;
  }

  async registerUser(event) {
    const data = formData(event);

    const res = await fetch(conf.apiUrl + "/user/register/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!res.ok)
      throw new Error({ message: "could not register at the moment" });

    return res;
  }

  async getDetails(token) {
    try {
      const resp = await fetch(conf.apiUrl + "/user/profile/", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      const respData = await resp.json();

      if (!resp.ok) throw new Error("Cannot fetch details at the moment");

      return respData;
    } catch (error) {
      throw new Error(error.message);
    }
  }

  async verify(id) {
    
   const resp = await fetch(conf.apiUrl + `/user/verify-email/${id}/`, {
   method: "GET",
   headers: {
    "Content-Type": "application/json",
   },
  }
  )

  if(!resp.ok) throw new Error("Cannot verify at the moment");

   return true;
  }
  
  async recents(token) {
    try {
      const resp = await fetch(conf.apiUrl + "/itinerary/recent/", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      const respData = await resp.json();

      if (!resp.ok) throw new Error("Cannot fetch details at the moment");

      return respData;
    } catch (error) {
      throw new Error("cannot find recents");
    }
  }
}

const user = new User();

export default user;
