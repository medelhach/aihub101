import { notFound } from "next/navigation";

import { StoryArticle } from "@/components/content/story-article";
import { getNews } from "@/services/api";

type NewsDetailPageProps = {
  params: Promise<{ slug: string }>;
};

export default async function NewsDetailPage({ params }: NewsDetailPageProps) {
  const { slug } = await params;
  let story;
  try {
    story = await getNews(slug);
  } catch {
    notFound();
  }
  return <StoryArticle story={story} />;
}
