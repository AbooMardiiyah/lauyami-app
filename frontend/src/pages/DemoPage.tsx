import Navbar from "@/components/Navbar";
import DemoSection from "@/components/DemoSection";
import Footer from "@/components/Footer";

const DemoPage = () => {
  return (
    <main className="min-h-screen bg-background">
      <Navbar />
      <div className="pt-16">
        <DemoSection />
      </div>
      <Footer />
    </main>
  );
};

export default DemoPage;
