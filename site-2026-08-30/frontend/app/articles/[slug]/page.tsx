import { notFound } from "next/navigation";

import { StoryArticle } from "@/components/content/story-article";
import { getArticle } from "@/services/api";

type ArticleDetailPageProps = {
  params: Promise<{ slug: string }>;
};

export default async function ArticleDetailPage({ params }: ArticleDetailPageProps) {
  const { slug } = await params;
  let story;
  try {
    story = await getArticle(slug);
  } catch {
    notFound();
  }
  return <StoryArticle story={story} />;
}
