import { HeroSection } from "@/components/home/HeroSection";
import { PublicMetrics } from "@/components/home/PublicMetrics";
import { VerificationDisclaimer } from "@/components/home/VerificationDisclaimer";
import { PollingStationSearch } from "@/components/search/PollingStationSearch";
import { getPublicMetrics, getPublicPollingStations } from "@/lib/api";

export default async function HomePage() {
  const pollingStations = await getPublicPollingStations();
  const metrics = getPublicMetrics(pollingStations);

  return (
    <main className="min-h-screen bg-slate-50">
      <HeroSection />
      <section className="mx-auto flex w-full max-w-7xl flex-col gap-8 px-4 py-8 sm:px-6 lg:px-8">
        <PublicMetrics metrics={metrics} />
        <PollingStationSearch pollingStations={pollingStations} />
        <VerificationDisclaimer />
      </section>
    </main>
  );
}
