import React from "react";
import ReactDOM from "react-dom/client";
import { AlertCircle, ArrowRight, CheckCircle2, ClipboardCheck, Copy, FileCheck2, FileSearch, Fingerprint, Info, Landmark, Search, SearchX, ShieldCheck } from "lucide-react";
import "./styles.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

type TimelineEvent = {
  acta_code?: string;
  polling_station_code?: string | null;
  event_type: string;
  timestamp: string;
  verification_status?: string | null;
  severity?: string | null;
  hash_proof?: { hash_value?: string | null } | null;
  public_document_status?: string | null;
  blockchain_anchor_proof?: { anchor_id?: string | null } | null;
};

type SearchResult = {
  acta_code: string;
  polling_station_code: string;
  municipality?: string | null;
  district?: string | null;
  verification_status: string;
  document_integrity_status: string;
  prep_validation_status: string;
  last_verified_at?: string | null;
};

function formatDateTime(value?: string | null) {
  if (!value) return "Not available";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Not available";
  return new Intl.DateTimeFormat("en", { dateStyle: "medium", timeStyle: "short" }).format(date);
}

function labelFromCode(value?: string | null) {
  if (!value) return "Not available";
  return value.toLowerCase().replaceAll("_", " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

function shortenHash(value?: string | null) {
  if (!value) return "Not available";
  if (value.length <= 20) return value;
  return `${value.slice(0, 12)}...${value.slice(-8)}`;
}

function sanitize(value: string) {
  return value.trim().replace(/[^\w\-.]/g, "");
}

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, { headers: { Accept: "application/json" } });
  if (!response.ok) throw new Error("PUBLIC_DATA_UNAVAILABLE");
  return response.json() as Promise<T>;
}

function navigate(path: string) {
  window.history.pushState({}, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
}

function usePath() {
  const [path, setPath] = React.useState(window.location.pathname + window.location.search);
  React.useEffect(() => {
    const handler = () => setPath(window.location.pathname + window.location.search);
    window.addEventListener("popstate", handler);
    return () => window.removeEventListener("popstate", handler);
  }, []);
  return path;
}

function Link({ href, children, className, ariaLabel }: { href: string; children: React.ReactNode; className?: string; ariaLabel?: string }) {
  return (
    <a
      href={href}
      className={className}
      aria-label={ariaLabel}
      onClick={(event) => {
        event.preventDefault();
        navigate(href);
      }}
    >
      {children}
    </a>
  );
}

function StatusBadge({ status }: { status?: string | null }) {
  const normalized = status ?? "NOT_AVAILABLE";
  const isDanger = normalized.includes("MISMATCH") || normalized.includes("FAILED") || normalized.includes("INCONSISTENCY");
  const isReview = normalized.includes("REVIEW") || normalized.includes("PENDING");
  const className = isDanger
    ? "border-danger-50 bg-danger-50 text-danger-600"
    : isReview
      ? "border-review-50 bg-review-50 text-review-600"
      : normalized.includes("VERIFIED") || normalized.includes("ANCHORED") || normalized.includes("MATCHED")
        ? "border-trust-100 bg-trust-50 text-trust-700"
        : "border-slate-200 bg-slate-50 text-slate-700";
  return <span className={`inline-flex items-center rounded-md border px-2.5 py-1 text-sm font-medium ${className}`}>{labelFromCode(normalized)}</span>;
}

function PublicHeader() {
  return (
    <header className="border-b border-border bg-surface">
      <div className="container-page flex min-h-16 items-center justify-between gap-6">
        <Link href="/" ariaLabel="ActaTrace home" className="flex items-center gap-2 font-semibold text-foreground">
          <span className="flex h-9 w-9 items-center justify-center rounded-md bg-trust-700 text-white">
            <ShieldCheck aria-hidden="true" className="h-5 w-5" />
          </span>
          <span>ActaTrace</span>
        </Link>
        <nav aria-label="Public navigation" className="hidden items-center gap-6 text-sm font-medium text-muted md:flex">
          <Link className="hover:text-foreground" href="/search">Search</Link>
          <Link className="hover:text-foreground" href="/verify">Verify fingerprint</Link>
          <Link className="hover:text-foreground" href="/about">About</Link>
        </nav>
        <Link href="/search" className="inline-flex items-center gap-2 rounded-md bg-trust-700 px-4 py-2 text-sm font-semibold text-white hover:bg-trust-600">
          <Search aria-hidden="true" className="h-4 w-4" />
          Search
        </Link>
      </div>
    </header>
  );
}

function PublicFooter() {
  return (
    <footer className="mt-20 border-t border-border bg-surface">
      <div className="container-page grid gap-4 py-8 text-sm text-muted md:grid-cols-[1fr_auto]">
        <p>ActaTrace verifies registered electoral evidence records. It does not count votes or replace the official electoral authority.</p>
        <p>Public verification portal</p>
      </div>
    </footer>
  );
}

function TrustBanner() {
  return (
    <aside className="border-y border-border bg-trust-50">
      <div className="container-page flex items-start gap-3 py-4 text-sm leading-6 text-trust-700">
        <Info aria-hidden="true" className="mt-0.5 h-5 w-5 shrink-0" />
        <p>ActaTrace does not count votes. It verifies whether registered evidence has remained consistent and whether public proof records support that verification.</p>
      </div>
    </aside>
  );
}

function ErrorState({ title = "Public data unavailable", message }: { title?: string; message: string }) {
  return (
    <div className="rounded-lg border border-danger-50 bg-danger-50 p-6 text-danger-600" role="alert">
      <div className="flex items-start gap-3">
        <AlertCircle aria-hidden="true" className="mt-0.5 h-5 w-5" />
        <div>
          <h2 className="text-base font-semibold">{title}</h2>
          <p className="mt-1 text-sm">{message}</p>
        </div>
      </div>
    </div>
  );
}

function EmptyState({ title = "No public records found", message }: { title?: string; message: string }) {
  return (
    <div className="rounded-lg border border-border bg-surface p-8 text-center">
      <SearchX aria-hidden="true" className="mx-auto h-8 w-8 text-muted" />
      <h2 className="mt-4 text-lg font-semibold text-foreground">{title}</h2>
      <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-muted">{message}</p>
    </div>
  );
}

function CopyButton({ value }: { value?: string | null }) {
  const [copied, setCopied] = React.useState(false);
  if (!value) return null;
  return (
    <button
      type="button"
      className="inline-flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1 text-sm font-medium text-foreground hover:bg-slate-50"
      onClick={async () => {
        await navigator.clipboard.writeText(value);
        setCopied(true);
        window.setTimeout(() => setCopied(false), 1600);
      }}
    >
      <Copy aria-hidden="true" className="h-4 w-4" />
      {copied ? "Copied" : "Copy"}
    </button>
  );
}

function ActaSearchForm() {
  const [actaCode, setActaCode] = React.useState("");
  const [pollingStationCode, setPollingStationCode] = React.useState("");
  const [error, setError] = React.useState("");

  function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const cleanActa = sanitize(actaCode);
    const cleanStation = sanitize(pollingStationCode);
    if (!cleanActa && !cleanStation) {
      setError("Enter an acta code or polling station code.");
      return;
    }
    const params = new URLSearchParams();
    if (cleanActa) params.set("acta_code", cleanActa);
    if (cleanStation) params.set("polling_station_code", cleanStation);
    navigate(`/search?${params.toString()}`);
  }

  return (
    <form onSubmit={onSubmit} className="institutional-card rounded-lg p-5" noValidate>
      <div className="grid gap-4 md:grid-cols-[1fr_1fr_auto]">
        <label className="block">
          <span className="text-sm font-medium text-foreground">Acta code</span>
          <input value={actaCode} onChange={(event) => setActaCode(event.target.value)} className="mt-1 w-full rounded-md border border-border px-3 py-2 text-sm" placeholder="ACTA-0456-B01" aria-label="Acta code" />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-foreground">Polling station code</span>
          <input value={pollingStationCode} onChange={(event) => setPollingStationCode(event.target.value)} className="mt-1 w-full rounded-md border border-border px-3 py-2 text-sm" placeholder="MXCMX-D12-S0456-B01" aria-label="Polling station code" />
        </label>
        <button type="submit" className="mt-6 inline-flex h-10 items-center justify-center gap-2 rounded-md bg-trust-700 px-5 text-sm font-semibold text-white hover:bg-trust-600">
          <Search aria-hidden="true" className="h-4 w-4" />
          Search
        </button>
      </div>
      {error ? <p className="mt-3 text-sm text-danger-600" role="alert">{error}</p> : null}
    </form>
  );
}

function HomePage() {
  return (
    <>
      <section className="bg-surface">
        <div className="container-page grid gap-10 py-16 md:grid-cols-[1fr_420px] md:items-center">
          <div>
            <h1 className="max-w-3xl text-4xl font-semibold leading-tight tracking-normal text-foreground md:text-5xl">Verify electoral evidence with traceable records.</h1>
            <p className="mt-5 max-w-2xl text-lg leading-8 text-muted">Search actas, review public traceability, and confirm whether registered documents match their verification proof.</p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link href="/search" className="inline-flex items-center justify-center gap-2 rounded-md bg-trust-700 px-5 py-3 text-sm font-semibold text-white hover:bg-trust-600">Search public records <ArrowRight aria-hidden="true" className="h-4 w-4" /></Link>
              <Link href="/verify" className="inline-flex items-center justify-center rounded-md border border-border px-5 py-3 text-sm font-semibold text-foreground hover:bg-slate-50">Verify a fingerprint</Link>
            </div>
          </div>
          <ActaSearchForm />
        </div>
      </section>
      <TrustBanner />
      <section className="container-page py-16">
        <h2 className="text-2xl font-semibold text-foreground">How public verification works</h2>
        <div className="mt-6 grid gap-4 md:grid-cols-3">
          {[
            [FileSearch, "Find the acta", "Search by acta code or polling station to locate public verification records."],
            [Fingerprint, "Review the fingerprint", "Confirm whether the registered document fingerprint remains consistent."],
            [CheckCircle2, "Read the timeline", "See public-safe traceability events without exposing internal sensitive data."]
          ].map(([Icon, title, text]) => (
            <article key={title as string} className="rounded-lg border border-border bg-surface p-6">
              <Icon aria-hidden="true" className="h-6 w-6 text-trust-700" />
              <h3 className="mt-4 font-semibold text-foreground">{title as string}</h3>
              <p className="mt-2 text-sm leading-6 text-muted">{text as string}</p>
            </article>
          ))}
        </div>
        <p className="mt-8 max-w-3xl text-sm leading-6 text-muted">This portal verifies evidence records and traceability. It does not replace official electoral authority decisions or publish restricted operational data.</p>
      </section>
    </>
  );
}

function SearchPage() {
  const [results, setResults] = React.useState<SearchResult[]>([]);
  const [failed, setFailed] = React.useState(false);
  const params = new URLSearchParams(window.location.search);
  const hasQuery = Boolean(params.toString());

  React.useEffect(() => {
    if (!hasQuery) return;
    fetchJson<SearchResult[]>(`/public/search?${params.toString()}`)
      .then((data) => {
        setResults(data);
        setFailed(false);
      })
      .catch(() => setFailed(true));
  }, [window.location.search]);

  return (
    <section className="container-page py-12">
      <div className="max-w-3xl">
        <h1 className="text-3xl font-semibold text-foreground">Search public verification records</h1>
        <p className="mt-3 text-sm leading-6 text-muted">Search by acta code or polling station code. Public results only include information safe for citizen review.</p>
      </div>
      <div className="mt-8"><ActaSearchForm /></div>
      <div className="mt-8">
        {failed ? <ErrorState title="Search service unavailable" message="The public search endpoint is not available yet. The frontend contract is ready for backend integration." /> : null}
        {!failed && hasQuery && results.length === 0 ? <EmptyState message="Try a different acta code or polling station code. Public records may still be pending publication." /> : null}
        {!failed && results.length > 0 ? (
          <div className="overflow-hidden rounded-lg border border-border bg-surface">
            <table className="w-full border-collapse text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase tracking-wide text-muted">
                <tr><th className="px-4 py-3">Acta</th><th className="px-4 py-3">Polling station</th><th className="px-4 py-3">District</th><th className="px-4 py-3">Verification</th><th className="px-4 py-3">Last checked</th></tr>
              </thead>
              <tbody>
                {results.map((result) => (
                  <tr key={result.acta_code} className="border-t border-border">
                    <td className="px-4 py-4 font-medium"><Link className="underline-offset-4 hover:underline" href={`/actas/${encodeURIComponent(result.acta_code)}`}>{result.acta_code}</Link></td>
                    <td className="px-4 py-4 text-muted">{result.polling_station_code}</td>
                    <td className="px-4 py-4 text-muted">{result.district ?? "Not available"}</td>
                    <td className="px-4 py-4"><StatusBadge status={result.verification_status} /></td>
                    <td className="px-4 py-4 text-muted">{formatDateTime(result.last_verified_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </div>
    </section>
  );
}

function ActaDetailPage({ actaCode }: { actaCode: string }) {
  const [events, setEvents] = React.useState<TimelineEvent[]>([]);
  const [failed, setFailed] = React.useState(false);

  React.useEffect(() => {
    fetchJson<TimelineEvent[]>(`/traceability/public/actas/${encodeURIComponent(actaCode)}`)
      .then((data) => {
        setEvents(data);
        setFailed(false);
      })
      .catch(() => setFailed(true));
  }, [actaCode]);

  const first = events[0];
  const fingerprint = events.find((event) => event.hash_proof?.hash_value)?.hash_proof?.hash_value;
  const hasProof = Boolean(fingerprint || events.some((event) => event.blockchain_anchor_proof?.anchor_id));
  const hasReview = events.some((event) => event.severity === "REVIEW_REQUIRED" || event.severity === "CRITICAL");

  if (failed) {
    return <section className="container-page py-12"><EmptyState title="Acta not found" message="No public-safe verification timeline was found for this acta code." /></section>;
  }

  return (
    <section className="container-page py-12">
      <section className="institutional-card rounded-lg p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <h1 className="text-3xl font-semibold tracking-normal text-foreground">{actaCode}</h1>
            <p className="mt-2 text-sm leading-6 text-muted">Polling station {first?.polling_station_code ?? "Not available"}. Public information is limited to verification records that are safe for citizen review.</p>
          </div>
          <StatusBadge status={hasReview ? "REQUIRES_REVIEW" : hasProof ? "PARTIALLY_VERIFIED" : "NOT_AVAILABLE"} />
        </div>
      </section>
      {hasReview ? <div className="mt-6"><ErrorState title="Public review notice" message="This acta has public traceability events that require review. Review the timeline before drawing conclusions." /></div> : null}
      <div className="mt-6 grid gap-5 lg:grid-cols-2">
        <ProofCard icon="status" title="Verification status" status={hasReview ? "REQUIRES_REVIEW" : hasProof ? "PARTIALLY_VERIFIED" : "NOT_AVAILABLE"} text="This summarizes the public evidence currently available for this acta." />
        <DocumentCard fingerprint={fingerprint} />
        <ProofCard icon="prep" title="PREP comparison" status={events.some((event) => event.event_type.includes("PREP")) ? "REQUIRES_REVIEW" : "NOT_AVAILABLE"} text="This shows whether preliminary result records match registered acta evidence when public data is available." />
        <ProofCard icon="proof" title="Independent verification proof" status={hasProof ? "ANCHORED" : "NOT_ANCHORED"} text="This proof helps confirm that the registered document fingerprint existed at a specific point in time. It does not store the document itself." reference={events.find((event) => event.blockchain_anchor_proof?.anchor_id)?.blockchain_anchor_proof?.anchor_id} />
      </div>
      <PublicTimeline events={events} />
    </section>
  );
}

function ProofCard({ title, status, text, reference, icon }: { title: string; status: string; text: string; reference?: string | null; icon: "status" | "prep" | "proof" }) {
  const Icon = icon === "prep" ? ClipboardCheck : icon === "proof" ? Landmark : ShieldCheck;
  return (
    <section className="rounded-lg border border-border bg-surface p-5">
      <div className="flex items-start gap-3">
        <Icon aria-hidden="true" className="mt-1 h-5 w-5 text-trust-700" />
        <div className="min-w-0 flex-1">
          <h2 className="text-lg font-semibold text-foreground">{title}</h2>
          <div className="mt-3"><StatusBadge status={status} /></div>
          <p className="mt-3 text-sm leading-6 text-muted">{text}</p>
          {reference ? <p className="mt-3 text-sm text-muted">Proof reference: <code className="rounded bg-slate-50 px-2 py-1">{shortenHash(reference)}</code></p> : null}
        </div>
      </div>
    </section>
  );
}

function DocumentCard({ fingerprint }: { fingerprint?: string | null }) {
  return (
    <section className="rounded-lg border border-border bg-surface p-5">
      <div className="flex items-start gap-3">
        <FileCheck2 aria-hidden="true" className="mt-1 h-5 w-5 text-trust-700" />
        <div className="min-w-0 flex-1">
          <h2 className="text-lg font-semibold text-foreground">Document proof</h2>
          <div className="mt-3"><StatusBadge status={fingerprint ? "VERIFIED" : "PENDING"} /></div>
          <dl className="mt-4 space-y-3 text-sm">
            <div>
              <dt className="font-medium text-foreground">Document fingerprint</dt>
              <dd className="mt-1 flex flex-wrap items-center gap-2 text-muted"><code className="break-all rounded bg-slate-50 px-2 py-1">{shortenHash(fingerprint)}</code><CopyButton value={fingerprint} /></dd>
            </div>
          </dl>
        </div>
      </div>
    </section>
  );
}

function PublicTimeline({ events }: { events: TimelineEvent[] }) {
  return (
    <section className="mt-6 rounded-lg border border-border bg-surface p-6">
      <h2 className="text-xl font-semibold text-foreground">Public traceability timeline</h2>
      {events.length === 0 ? <p className="mt-4 text-sm text-muted">No public timeline events are available yet.</p> : null}
      <ol className="mt-6 space-y-4">
        {events.map((event, index) => (
          <li key={`${event.event_type}-${event.timestamp}-${index}`} className="grid gap-3 border-l-2 border-border pl-4 sm:grid-cols-[180px_1fr]">
            <time className="text-sm text-muted">{formatDateTime(event.timestamp)}</time>
            <div>
              <div className="flex flex-wrap items-center gap-2"><CheckCircle2 aria-hidden="true" className="h-4 w-4 text-trust-700" /><h3 className="font-medium text-foreground">{labelFromCode(event.event_type)}</h3><StatusBadge status={event.verification_status ?? event.severity} /></div>
              <p className="mt-2 text-sm leading-6 text-muted">Public traceability record for {event.polling_station_code ?? "this polling station"}. Sensitive internal details are not shown.</p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}

function VerifyPage() {
  const [hashValue, setHashValue] = React.useState("");
  const [error, setError] = React.useState("");
  const [result, setResult] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const cleanHash = hashValue.trim().toLowerCase();
    if (!/^[a-fA-F0-9]{64}$/.test(cleanHash)) {
      setError("Enter a valid 64-character document fingerprint.");
      setResult(null);
      return;
    }
    setLoading(true);
    setError("");
    try {
      setResult(await fetchJson(`/blockchain/verify/hash/${encodeURIComponent(cleanHash)}`));
    } catch {
      setError("The verification service is unavailable. Please try again later.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="container-page grid gap-8 py-12 lg:grid-cols-[1fr_380px]">
      <div>
        <h1 className="text-3xl font-semibold text-foreground">Verify a document fingerprint</h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-muted">Paste a document fingerprint to check whether a public proof record exists. Technical values are shown for auditors, but the result is explained in plain language.</p>
        <form onSubmit={onSubmit} className="institutional-card mt-8 rounded-lg p-6" noValidate>
          <label className="block">
            <span className="text-sm font-medium text-foreground">Document fingerprint</span>
            <textarea value={hashValue} onChange={(event) => setHashValue(event.target.value)} className="mt-2 min-h-28 w-full rounded-md border border-border px-3 py-2 font-mono text-sm" placeholder="Paste the 64-character document fingerprint" aria-label="Document fingerprint" />
          </label>
          <button type="submit" className="mt-4 inline-flex items-center justify-center gap-2 rounded-md bg-trust-700 px-5 py-2.5 text-sm font-semibold text-white hover:bg-trust-600" disabled={loading}><Fingerprint aria-hidden="true" className="h-4 w-4" />{loading ? "Checking" : "Verify fingerprint"}</button>
        </form>
        {error ? <div className="mt-5"><ErrorState title="Verification unavailable" message={error} /></div> : null}
        {result ? (
          <section className="mt-5 rounded-lg border border-border bg-surface p-6" aria-live="polite">
            <h2 className="text-xl font-semibold text-foreground">{result.exists || result.verification_status === "VERIFIED" ? "Fingerprint found" : "Fingerprint not found"}</h2>
            <p className="mt-2 text-sm leading-6 text-muted">{result.exists || result.verification_status === "VERIFIED" ? "A public proof record exists for this document fingerprint." : "No public proof record was found for this fingerprint."}</p>
            <dl className="mt-5 grid gap-4 text-sm md:grid-cols-2">
              <div><dt className="font-medium text-foreground">Document fingerprint</dt><dd className="mt-1 text-muted">{shortenHash(result.hash_value ?? hashValue)}</dd></div>
              <div><dt className="font-medium text-foreground">Proof reference</dt><dd className="mt-1 text-muted">{shortenHash(result.transaction_hash ?? result.transaction_id ?? result.anchor_id)}</dd></div>
            </dl>
          </section>
        ) : null}
      </div>
      <section className="rounded-lg border border-border bg-surface p-6">
        <h2 className="text-xl font-semibold text-foreground">How verification works</h2>
        <div className="mt-5 space-y-4">
          {["A document fingerprint is created from the registered file.", "The fingerprint is compared with public proof records.", "The portal explains whether the evidence remains consistent."].map((text, index) => (
            <div key={text} className="rounded-lg border border-border p-4"><span className="flex h-8 w-8 items-center justify-center rounded-md bg-trust-50 font-semibold text-trust-700">{index + 1}</span><p className="mt-3 text-sm leading-6 text-muted">{text}</p></div>
          ))}
        </div>
      </section>
    </section>
  );
}

function AboutPage() {
  const sections = [
    ["What ActaTrace verifies", "Registered acta evidence, document fingerprints, public traceability events, PREP comparison status, and independent proof references."],
    ["What it does not verify", "ActaTrace does not cast votes, count votes, manage ballot secrecy, or replace official electoral decisions."],
    ["How document fingerprints work", "A fingerprint is generated from the document contents. If the file changes, the fingerprint changes."],
    ["Why files are not stored in proof records", "Public proof records store fingerprints and references, not full documents or private operational data."],
    ["How public traceability works", "The portal shows safe lifecycle events while removing internal user IDs, IP addresses, private notes, and storage paths."],
    ["System limits", "Public data may be incomplete while institutional review is still in progress. Review notices should be interpreted carefully."]
  ];
  return (
    <section className="container-page py-12">
      <div className="max-w-3xl">
        <h1 className="text-3xl font-semibold text-foreground">About ActaTrace public verification</h1>
        <p className="mt-4 text-sm leading-6 text-muted">ActaTrace helps citizens review whether registered electoral evidence remains consistent. It focuses on document integrity, traceability, and public proof records.</p>
      </div>
      <div className="mt-8 grid gap-5 md:grid-cols-2">
        {sections.map(([title, text]) => <article key={title} className="rounded-lg border border-border bg-surface p-6"><h2 className="font-semibold text-foreground">{title}</h2><p className="mt-2 text-sm leading-6 text-muted">{text}</p></article>)}
      </div>
    </section>
  );
}

function App() {
  const path = usePath();
  const pathname = path.split("?")[0];
  let page: React.ReactNode;
  if (pathname === "/") page = <HomePage />;
  else if (pathname === "/search") page = <SearchPage />;
  else if (pathname === "/verify") page = <VerifyPage />;
  else if (pathname === "/about") page = <AboutPage />;
  else if (pathname.startsWith("/actas/")) page = <ActaDetailPage actaCode={decodeURIComponent(pathname.replace("/actas/", ""))} />;
  else page = <section className="container-page py-12"><EmptyState title="Page not found" message="The requested public page is not available." /></section>;

  return (
    <div className="min-h-screen">
      <PublicHeader />
      <main>{page}</main>
      <PublicFooter />
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
