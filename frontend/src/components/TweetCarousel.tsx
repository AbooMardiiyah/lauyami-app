import { useEffect, useState } from "react";
import tweet1 from "@/assets/tweet-1.png";
import tweet2 from "@/assets/tweet-2.png";
import tweet3 from "@/assets/tweet-3.png";

const tweets = [tweet1, tweet2, tweet3];

const TweetCarousel = () => {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % tweets.length);
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  return (
    <section id="problem" className="py-16 md:py-24 bg-foreground">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <span className="inline-block px-4 py-2 rounded-full bg-secondary/20 text-secondary text-sm font-medium mb-4">
            Real Stories
          </span>
          <h2 className="text-3xl md:text-4xl font-bold text-primary-foreground mb-4">
            This Happens Every Day in Nigeria
          </h2>
          <p className="text-lg text-primary-foreground/70 max-w-2xl mx-auto">
            Millions of tenants sign agreements they don't understand. The consequences are devastating.
          </p>
        </div>

        {/* Carousel */}
        <div className="relative max-w-2xl mx-auto">
          <div className="overflow-hidden rounded-xl">
            <div
              className="flex transition-transform duration-500 ease-in-out"
              style={{ transform: `translateX(-${currentIndex * 100}%)` }}
            >
              {tweets.map((tweet, index) => (
                <div key={index} className="min-w-full px-2">
                  <img
                    src={tweet}
                    alt={`Real tenant story ${index + 1}`}
                    className="w-full rounded-xl shadow-lg"
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Dots */}
          <div className="flex justify-center gap-2 mt-6">
            {tweets.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentIndex(index)}
                className={`w-3 h-3 rounded-full transition-all ${
                  index === currentIndex
                    ? "bg-secondary w-8"
                    : "bg-primary-foreground/30 hover:bg-primary-foreground/50"
                }`}
              />
            ))}
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-16 max-w-4xl mx-auto">
          <div className="text-center">
            <div className="text-4xl md:text-5xl font-bold text-secondary mb-2">30%+</div>
            <p className="text-sm text-primary-foreground/70">Nigerian adults are non-literate</p>
          </div>
          <div className="text-center">
            <div className="text-4xl md:text-5xl font-bold text-secondary mb-2">₦200k+</div>
            <p className="text-sm text-primary-foreground/70">Average lawyer consultation fee</p>
          </div>
          <div className="text-center">
            <div className="text-4xl md:text-5xl font-bold text-secondary mb-2">70%</div>
            <p className="text-sm text-primary-foreground/70">Sign without understanding</p>
          </div>
          <div className="text-center">
            <div className="text-4xl md:text-5xl font-bold text-secondary mb-2">1000s</div>
            <p className="text-sm text-primary-foreground/70">Illegal evictions yearly</p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default TweetCarousel;
