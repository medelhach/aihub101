import type { StoryDetail } from "@/services/api";

type StoryArticleProps = {
  story: StoryDetail;
};

export function StoryArticle({ story }: StoryArticleProps) {
  return (
    <article className="mx-auto w-full max-w-3xl">
      <p className="text-xs font-semibold tracking-[0.2em] text-slate-500 uppercase">
        {story.section === "news" ? "News" : "Article"} · {story.source_name}
      </p>
      <h1 className="mt-3 text-4xl font-semibold tracking-tight text-slate-950">
        {story.headline}
      </h1>
      <p className="mt-4 text-lg leading-8 text-slate-700">{story.dek}</p>
      <p className="mt-4 text-sm text-slate-500">
        {story.dateline}
        {story.author ? ` · ${story.author}` : ""} · {story.word_count} words
      </p>
      <p className="mt-8 text-lg leading-8 text-slate-800">{story.lead}</p>
      {story.sections.map((section) => (
        <section key={section.heading} className="mt-10">
          <h2 className="text-2xl font-semibold tracking-tight">{section.heading}</h2>
          <div className="mt-3 whitespace-pre-wrap text-base leading-8 text-slate-700">
            {section.body}
          </div>
        </section>
      ))}
      <aside className="mt-12 rounded-2xl border border-slate-200 bg-slate-50 p-6 text-sm leading-6 text-slate-600">
        This Hub brief is an original structured account of attributed facts. Read the
        publisher&apos;s original:{" "}
        <a className="font-medium text-slate-950 underline" href={story.source_url} rel="noreferrer">
          {story.source_name}
        </a>
        .
      </aside>
    </article>
  );
}
