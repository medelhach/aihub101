import { StoryImage } from "@/components/content/story-image";
import type { StoryDetail } from "@/services/api";

type StoryArticleProps = {
  story: StoryDetail;
};

export function StoryArticle({ story }: StoryArticleProps) {
  return (
    <article className="mx-auto w-full max-w-3xl px-4 py-10 sm:px-6">
      <p className="text-[0.7rem] font-semibold tracking-[0.28em] text-crimson uppercase">
        {story.section === "news" ? "News" : "Article"} · {story.source_name}
      </p>
      <h1 className="font-display mt-3 text-4xl leading-tight text-balance md:text-5xl">
        {story.headline}
      </h1>
      <p className="mt-5 text-xl leading-8 text-ink/75">{story.dek}</p>
      <p className="mt-4 text-sm text-ink/50">
        {story.dateline}
        {story.author ? ` · ${story.author}` : ""} · {story.word_count} words
      </p>
      <div className="mt-8 overflow-hidden">
        <StoryImage story={story} className="aspect-[16/9]" priority />
      </div>
      <p className="font-display mt-10 text-2xl leading-9 text-ink">{story.lead}</p>
      {story.sections.map((section) => (
        <section key={section.heading} className="mt-10">
          <h2 className="font-display text-2xl tracking-tight">{section.heading}</h2>
          <div className="mt-3 whitespace-pre-wrap text-base leading-8 text-ink/80">
            {section.body}
          </div>
        </section>
      ))}
      {story.key_facts.length > 0 ? (
        <aside className="mt-12 border border-rule bg-cream p-6">
          <p className="text-[0.7rem] font-semibold tracking-[0.24em] text-crimson uppercase">
            Key facts
          </p>
          <ul className="mt-3 list-disc space-y-2 pl-5 text-sm leading-6 text-ink/80">
            {story.key_facts.map((fact) => (
              <li key={fact}>{fact}</li>
            ))}
          </ul>
        </aside>
      ) : null}
      <aside className="mt-8 border-t border-rule pt-6 text-sm leading-6 text-ink/70">
        This desk brief is an original structured account of attributed facts. Read the
        publisher&apos;s original:{" "}
        <a className="font-medium text-crimson underline" href={story.source_url} rel="noreferrer">
          {story.source_name}
        </a>
        .
      </aside>
    </article>
  );
}
