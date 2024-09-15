import Cookies from "js-cookie";
import { useEffect, useState } from "react";
import user from "../services/authentication";
import Card from "./Card";

export default function Recents() {
  const [recents, setRecents] = useState(null);
  useEffect(() => {
    user.recents(Cookies.get("access_token")).then((data) => {
      console.log(data);
      setRecents(data.data);
    });
  }, []);

  return !recents ? (
    <h3 className="text-center font-medium text-2xl">Your recent dreams</h3>
  ) : (
    <div className="mt-40 p-2 border-2  shadow-md">
      {recents.map((itinerary, ind) => {
        return <Card key={ind} itinerary={itinerary} />;
      })}
    </div>
    // <>asd</>
  );
}
