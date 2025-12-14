import Navbar from "@/components/Navbar";
import HeroSection from "@/components/HeroSection";
import TweetCarousel from "@/components/TweetCarousel";
import Footer from "@/components/Footer";

const Index = () => {
  return (
    <main className="min-h-screen bg-background">
      <Navbar />
      <HeroSection />
      <TweetCarousel />
      <Footer />
    </main>
  );
};

export default Index;
