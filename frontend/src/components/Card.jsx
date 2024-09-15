import logo from "../assets/logo.png";
import { formatDate } from "../services/dateFormat";

export default function Card({ itinerary }) {
  return (
    <div className="w-4/5 h-52 mx-auto bg-white shadow-md shadow-teal-200 rounded-xl  m-6 flex transition-transform duration-300 ease-in-out  hover:scale-[1.01] hover:shadow-lg border-2 border-teal-400">
      <img
        className="w-1/3 h-auto object-cover rounded"
        src={itinerary.image_url || logo}
        alt={itinerary.name}
      />
      <div className="pl-9 pt-5 w-2/3">
        <p className="text-xl mb-4 capitalize inline-flex">{itinerary.name}</p>

        <div className="text-sm mt-2 flex items-center justify-between w-60">
          <svg
            className="w-4 h-4 hover:drop-shadow-md"
            xmlns="http://www.w3.org/2000/svg"
            fill="currentColor"
            viewBox="0 0 20 20">
            <path d="M20 4a2 2 0 0 0-2-2h-2V1a1 1 0 0 0-2 0v1h-3V1a1 1 0 0 0-2 0v1H6V1a1 1 0 0 0-2 0v1H2a2 2 0 0 0-2 2v2h20V4ZM0 18a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8H0v10Zm5-8h10a1 1 0 0 1 0 2H5a1 1 0 0 1 0-2Z" />
          </svg>
          <span>{formatDate(itinerary.start_date)}</span>
          &rarr;
          <span>{formatDate(itinerary.end_date)}</span>
        </div>
      </div>
    </div>
  );
}
