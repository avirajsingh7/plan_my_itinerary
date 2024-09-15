import { createContext, useContext, useState } from "react";
const ItineraryContext = createContext();

export const useItinerary = () => {
  return useContext(ItineraryContext);
};

export default function ItineraryProvider({ children }) {
  const [itinerary, setItinerary] = useState(null);

  return (
    <ItineraryContext.Provider value={{ itinerary, setItinerary }}>
      {children}
    </ItineraryContext.Provider>
  );
}
