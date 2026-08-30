import { ModelCard } from "@/components/content/model-card";
import { listModels, type ModelSummary } from "@/services/api";

export const metadata = {
  title: "AI Models",
  description: "Structured profiles for more than fifty important AI models.",
};

export default async function ModelsPage() {
  let models: ModelSummary[] = [];
  try {
    models = await listModels();
  } catch {
    models = [];
  }

  return (
    <div className="flex w-full flex-col gap-8">
      <header className="max-w-2xl">
        <h1 className="text-3xl font-semibold tracking-tight">AI models</h1>
        <p className="mt-3 text-base leading-7 text-slate-600">
          {models.length} models covering language, reasoning, multimodal, image, video,
          audio, and embeddings. Figures are indicative public specifications and can change.
        </p>
      </header>
      {models.length === 0 ? (
        <p className="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-sm text-slate-600">
          The catalog appears after the API can reach PostgreSQL and complete startup seeding.
        </p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {models.map((model) => (
            <ModelCard key={model.slug} model={model} />
          ))}
        </div>
      )}
    </div>
  );
}
