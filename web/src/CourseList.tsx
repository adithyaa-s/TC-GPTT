import React, { useState, useMemo } from "react";
import { Box, Input, Stack, Button, Spinner } from "./ui";
import CourseCard from "./CourseCard";

export default function CourseList({ courses, onSelect }) {
  const [search, setSearch] = useState("");
  const filtered = useMemo(() => {
    return courses.filter((c) =>
      c.name.toLowerCase().includes(search.toLowerCase())
    );
  }, [search, courses]);

  if (!courses) return <Spinner />;

  return (
    <Box css={{ p: "$4" }}>
      <Stack gap="$3">
        <Input
          placeholder="Search courses…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        {filtered.map((c) => (
          <CourseCard key={c.id} course={c} onClick={() => onSelect(c)} />
        ))}
      </Stack>
    </Box>
  );
}
