import { Chrono } from "react-chrono";
import Logo from "../assets/logo.png";

export default function Timeline({ activities }) {
  return (
    <>
      {Object.keys(activities).map((Day, ind) => {
        return (
          <div key={ind}>
            <h1 style={{ textAlign: "center", fontWeight: 600, fontSize: 50 }}>
              Day {Day}
            </h1>
            <Chrono
              items={activities[Day].map((activity) => {
                return {
                  title: activity.time_of_day.toUpperCase(),
                  cardTitle: activity.name,
                  cardSubtitle: `${activity.place_details.ranking}`,
                  cardDetailedText: [
                    `<div>`,
                    `Duration: <strong>${activity.duration}</strong>`,
                    `${activity.description}`,
                    `<strong>${activity.place_details.address_string}</strong>`,
                    `</div>`,
                  ],

                  media: {
                    name: `${activity.name}`,
                    type: "IMAGE",
                    source: {
                      url: activity.place_images[0]?.original || Logo,
                    },
                  },
                };
              })}
              mode="VERTICAL_ALTERNATING"
              highlightCardsOnHover
              parseDetailsAsHTML
              disableToolbar
              theme={{
                primary: "#11756e",
                secondary: "#fff",
                titleColor: "#11756e",
                titleColorActive: "#11756e",
                cardSubtitleColor: "#11756e",
                cardTitleColor: "#11756e",
                cardDetailsColor: "#11756e",
              }}
            />
          </div>
        );
      })}
    </>
  );
}
