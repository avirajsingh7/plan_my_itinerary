import Timeline from "../components/Timeline";
import { useItinerary } from "../contexts/ItineraryContext";
import { formatDate } from "../services/dateFormat";

export default function TimelinePage() {
  const { itinerary } = useItinerary();

  return (
    <section className="text-teal-700">
      <div className="p-6 text-center shadow-lg shadow-teal-100 z-20 border-2 border-teal-400 rounded-b-full">
        <span className="text-4xl capitalize">{itinerary?.name}</span>
        <div className="w-1/5 text-sm mx-auto mt-5 flex justify-between items-center">
          <span>{formatDate(itinerary?.start_date)}</span>
          &rarr;
          <span>{formatDate(itinerary?.end_date)}</span>
        </div>
      </div>
      <Timeline activities={itinerary?.activities} />
    </section>
  );
}
