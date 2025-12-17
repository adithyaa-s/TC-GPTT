import React, { useEffect, useState } from "react";
import { Box, Spinner } from "./ui";

export default function OutlineTab({ courseId }) {
  const [outline, setOutline] = useState(null);

  useEffect(() => {
    // Your MCP tool to fetch combined outline
    window.openai
      ?.callTool("tc_get_course_lessons", { courseId })
      .then((res) => setOutline(res));
  }, [courseId]);

  if (!outline) return <Spinner />;

  return (
    <Box>
      {outline.chapters?.map((ch) => (
        <Box key={ch.sectionId}>
          <strong>{ch.name}</strong>
          {ch.lessons?.map((l) => (
            <Box key={l.id} css={{ ml: "$2" }}>
              {l.name}
            </Box>
          ))}
        </Box>
      ))}
    </Box>
  );
}
