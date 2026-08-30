import Link from "next/link";

import { catalogCover } from "@/lib/story-media";
import type { ModelSummary } from "@/services/api";

type ModelCardProps = {
  model: ModelSummary;
};

export function ModelCard({ model }: ModelCardProps) {
  return (
    <article className="flex h-full flex-col overflow-hidden border border-rule bg-cream">
      <Link href={`/models/${model.slug}`} className="block overflow-hidden">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={catalogCover(model.slug)}
          alt=""
          className="aspect-[16/9] w-full object-cover transition duration-500 hover:scale-[1.03]"
        />
      </Link>
      <div className="flex flex-1 flex-col p-5">
        <p className="text-[0.65rem] font-semibold tracking-[0.22em] text-crimson uppercase">
          {model.provider}
        </p>
        <h2 className="font-display mt-2 text-xl tracking-tight">
          <Link href={`/models/${model.slug}`} className="hover:text-crimson">
            {model.name}
          </Link>
        </h2>
        <p className="mt-2 text-sm text-ink/65">
          {model.modality}
          {model.context_window_tokens
            ? ` · ${model.context_window_tokens.toLocaleString()} context`
            : ""}
        </p>
        <ul className="mt-4 flex flex-wrap gap-2 text-xs">
          {model.open_weights ? (
            <li className="bg-ink px-2 py-1 text-paper">Open weights</li>
          ) : (
            <li className="bg-rule/60 px-2 py-1 text-ink">API / hosted</li>
          )}
          {model.reasoning ? <li className="bg-crimson/10 px-2 py-1 text-crimson">Reasoning</li> : null}
          {model.multimodal ? <li className="border border-rule px-2 py-1">Multimodal</li> : null}
        </ul>
      </div>
    </article>
  );
}
