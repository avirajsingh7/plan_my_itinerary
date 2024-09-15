import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { conf } from "../conf";
import { useItinerary } from "../contexts/ItineraryContext";
import handleSearch from "../services/search";
import Loader from "./Loader";

const tags = [
  "Attractions",
  "Tourist places",
  "Hidden Gems",
  "Herritage",
  "Shopping",
  "Cultural",
  "Landmarks",
  "OutdoorsWine",
  "Adventure",
  "Arts",
  "Culture",
  "Architecture",
  "Photography Spots",
];

export default function SearchBar() {
  const { setItinerary } = useItinerary();
  const navigate = useNavigate();
  const [destination, setdestination] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [debounceTimer, setDebounceTimer] = useState(null);
  const [selectedTag, setSelectedTag] = useState([]);
  const [loader, setLoader] = useState(false);

  useEffect(() => {
    if (destination.length > 2) {
      if (debounceTimer) {
        clearTimeout(debounceTimer);
      }

      const timer = setTimeout(async () => {
        try {
          const response = await fetch(
            `https://api.geoapify.com/v1/geocode/autocomplete?text=${destination}&apiKey=${conf.geoapifyApiKey}`
          );
          const data = await response.json();

          if (data.features && Array.isArray(data.features)) {
            const newSuggestions = data.features.map(
              (feature) => feature.properties.formatted
            );
            setSuggestions(newSuggestions);
          } else {
            console.log("No results found");
            setSuggestions([]);
          }
        } catch (error) {
          console.error("Error fetching suggestions:", error);
          setSuggestions([]);
        }
      }, 150);

      setDebounceTimer(timer);
    } else {
      setSuggestions([]);
    }
  }, [destination]);

  const submitHandler = (e) => {
    setLoader(true);
    handleSearch(e, selectedTag)
      .then((resp) => resp.json())
      .then((data) => {
        setItinerary(data.data);
        setLoader(false);
        navigate("/timeline");
      })
      .catch((error) => {
        console.log(error);
      });
  };

  return loader ? (
    <>
      <Loader />
      <div className="flex flex-col gap-4 justify-center items-center">
        <h3 className="text-xl font-semibold">
          🤩 Creating Your Perfect Journey
        </h3>
        <p>
          <strong>Hang Tight</strong> while we gather the best recommendations
          for <strong>Your Next Trip</strong> It will only take a few seconds.
        </p>
      </div>
    </>
  ) : (
    <form onSubmit={(e) => submitHandler(e)} className="mx-auto mt-20 w-3/5">
      <input
        type="text"
        name="destination"
        value={destination}
        onChange={(e) => setdestination(e.target.value)}
        list="suggestions"
        required
        placeholder="Search destinations..."
        className="px-4 py-2 my-9 border border-gray-300 rounded-full shadow w-full focus:ring-2 focus:ring-teal-400 focus:outline-none focus:border-transparent hover:ring-2 hover:ring-teal-400"
      />
      <datalist id="suggestions">
        {suggestions.map((suggestion, index) => (
          <option value={suggestion} key={index} />
        ))}
      </datalist>

      <div
        id="date-range-picker"
        className="flex flex-col md:flex-row items-center justify-between gap-8">
        <div className="relative w-full">
          <label htmlFor="start_date" className="my-2 text-center">
            From
            <div className="absolute inset-y-11 start-0 flex items-center justify-center ps-3 pointer-events-none">
              <svg
                className="w-5 h-5 text-teal-400"
                xmlns="http://www.w3.org/2000/svg"
                fill="currentColor"
                viewBox="0 0 20 20">
                <path d="M20 4a2 2 0 0 0-2-2h-2V1a1 1 0 0 0-2 0v1h-3V1a1 1 0 0 0-2 0v1H6V1a1 1 0 0 0-2 0v1H2a2 2 0 0 0-2 2v2h20V4ZM0 18a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8H0v10Zm5-8h10a1 1 0 0 1 0 2H5a1 1 0 0 1 0-2Z" />
              </svg>
            </div>
            <input
              required
              id="start_date"
              name="start_date"
              type="date"
              className="border shadow text-gray-900 rounded-lg focus:ring-teal-500 focus:border-teal-500 block w-full ps-10 p-2.5"
            />
          </label>
        </div>
        <div className="relative w-full">
          <label htmlFor="end_date" className="my-2 text-center">
            To
            <div className="absolute inset-y-11 start-0 flex items-center justify-center ps-3 pointer-events-none">
              <svg
                className="w-5 h-5 text-teal-400"
                xmlns="http://www.w3.org/2000/svg"
                fill="currentColor"
                viewBox="0 0 20 20">
                <path d="M20 4a2 2 0 0 0-2-2h-2V1a1 1 0 0 0-2 0v1h-3V1a1 1 0 0 0-2 0v1H6V1a1 1 0 0 0-2 0v1H2a2 2 0 0 0-2 2v2h20V4ZM0 18a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8H0v10Zm5-8h10a1 1 0 0 1 0 2H5a1 1 0 0 1 0-2Z" />
              </svg>
            </div>
            <input
              required
              id="end_date"
              name="end_date"
              type="date"
              className="border text-gray-900 rounded-lg focus:ring-teal-300 shadow block w-full ps-10 p-2.5"
            />
          </label>
        </div>
      </div>

      <div className="flex flex-wrap justify-center gap-3 text-center my-14">
        {tags.map((tag, index) => {
          return (
            <span
              key={index}
              className={`px-4 py-2 rounded-full hover:ring-2 hover:ring-teal-400 cursor-pointer border shadow ${
                selectedTag.includes(tag)
                  ? "ring-2 ring-teal-300"
                  : "border-gray-300"
              }`}>
              <label htmlFor={tag} className="cursor-pointer w-full h-full">
                {tag}
                <input
                  type="checkbox"
                  name={tag}
                  id={tag}
                  className="appearance-none"
                  onChange={(e) =>
                    setSelectedTag(
                      e.target.checked
                        ? [...selectedTag, e.target.name]
                        : selectedTag.filter((t) => t !== e.target.name)
                    )
                  }
                />
              </label>
            </span>
          );
        })}
      </div>

      <div className="w-full flex justify-center">
        <button
          type="submit"
          className="px-6 py-3 text-xl bg-teal-500 shadow-teal-300 w-3/5 text-white rounded-full hover:bg-teal-600 hover:shadow-md hover:shadow-teal-200 transition-transform duration-200 ease-in-out hover:scale-[1.02] focus:outline-none focus:ring-2 focus:ring-teal-500">
          Generate
        </button>
      </div>
    </form>
  );
}
