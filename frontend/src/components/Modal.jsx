import Card from "./Card";

export default function Modal({ data }) {
  return (
    <section className="absolute min-h-screen top-10 left-10 text-black bg-slate-200 w-11/12 py-5 px-5">
      <div className="flex h-3 w-full justify-between items-center">
        <span> Start Data: {data.start_date}</span>
        <span>End Date: {data.end_date}</span>
        <span> Total Days: {data.total_days}</span>
      </div>
      <section className="mx-auto mt-28 w-11/12 grid md:grid-cols-3 gap-4 xl:grid-cols-4">
        {data.activities.map((activity, ind) => (
          <Card key={ind} activity={activity} />
        ))}
      </section>
    </section>
  );
}
