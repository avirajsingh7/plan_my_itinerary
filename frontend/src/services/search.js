import Cookies from "js-cookie";
import { conf } from "../conf";
import { formData } from "./authentication";

const totalDays = (start, end) => {
  const startDate = new Date(start);
  const endDate = new Date(end);

  const daysDiff = (endDate - startDate) / (1000 * 60 * 60 * 24);
  const roundedDaysDiff = Math.round(daysDiff)+1;

  return roundedDaysDiff;
};

export default async function handleSearch(event, selectedTag) {
  const token = Cookies.get("access_token");
  const data = formData(event);

  if (selectedTag.length === 0) selectedTag = ["Tourist Places"];

  const requestData = {
    start_date: data.start_date,
    end_date: data.end_date,
    num_of_days: totalDays(data.start_date, data.end_date),
    destination: data.destination,
    must_includes: selectedTag,
  };

  const res = await fetch(conf.apiUrl + "/itinerary/generate/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(requestData),
  });

  if (!res.ok)
    throw new Error({ message: "Cannot proceed with the query. try again" });

  return res;
}

export async function handleRecent(id) {
  const token = Cookies.get("access_token");

  const resp = await fetch(`${conf.apiUrl}/itinerary/${id}/`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  });

  if (!resp.ok)
    throw new Error({ message: "Cannot proceed with the query. try again" });

  return resp;
}
