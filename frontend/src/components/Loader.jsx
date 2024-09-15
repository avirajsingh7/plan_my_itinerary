export default function Loader() {
  return (
    <div className="loader relative mx-auto max-w-lg h-80 overflow-hidden">
      <div className="plane absolute w-full mx-auto">
        <img
          src="https://zupimages.net/up/19/34/4820.gif"
          className="plane-img animate-spin-slow mx-auto"
          alt="plane"
        />
      </div>
      <div className="earth-wrapper absolute w-full pt-10 mx-auto">
        <div className="earth mx-auto w-40 h-40 bg-[url('https://zupimages.net/up/19/34/6vlb.gif')] bg-cover rounded-full animate-earth-spin border border-gray-300"></div>
      </div>
    </div>
  );
}
