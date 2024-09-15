import Timeline from "../components/Timeline";
import { useItinerary } from "../contexts/ItineraryContext";
import { formatDate } from "../services/dateFormat";

export default function TimelinePage() {
  const { itinerary } = useItinerary();
  const storedItinerary = JSON.parse(localStorage.getItem("itinerary"));

  const currentItinerary = itinerary || storedItinerary;

  return (
    <section className="text-teal-700">
      <div className="p-6 text-center shadow-lg shadow-teal-100 z-20 border-2 border-teal-400 rounded-b-full mb-10">
        <span className="text-4xl capitalize">{currentItinerary?.name}</span>
        <div className="w-1/5 text-sm mx-auto mt-5 flex justify-between items-center">
          <span>{formatDate(currentItinerary?.start_date)}</span>
          &rarr;
          <span>{formatDate(currentItinerary?.end_date)}</span>
        </div>
      </div>
      <Timeline activities={currentItinerary?.activities} />
    </section>
  );
}
