import React, { useEffect, useState } from "react";
import { Box, Spinner } from "./ui";

export default function ChaptersTab({ courseId }) {
  const [chapters, setChapters] = useState(null);

  useEffect(() => {
    window.openai
      ?.callTool("tc_get_course_lessons", { courseId })
      .then((res) => setChapters(res.chapters || []));
  }, [courseId]);

  if (!chapters) return <Spinner />;

  return <Box>{chapters.map((c) => c.name)}</Box>;
}

