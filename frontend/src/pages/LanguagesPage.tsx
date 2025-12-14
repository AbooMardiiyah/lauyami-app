import Navbar from "@/components/Navbar";
import LanguagesSection from "@/components/LanguagesSection";
import Footer from "@/components/Footer";

const LanguagesPage = () => {
  return (
    <main className="min-h-screen bg-background">
      <Navbar />
      <div className="pt-16">
        <LanguagesSection />
      </div>
      <Footer />
    </main>
  );
};

export default LanguagesPage;
