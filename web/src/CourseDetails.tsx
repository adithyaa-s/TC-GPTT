import React, { useEffect, useState } from "react";
import { Box, Button, Badge } from "./ui";
import LessonsTab from "./LessonsTab";
import ChaptersTab from "./ChaptersTab";
import OutlineTab from "./OutlineTab";
import CourseForm from "./CourseForm";
import ConfirmDialog from "./ConfirmDialog";

export default function CourseDetails({ course, goBack, push }) {
  const [tab, setTab] = useState("details");
  const [showEdit, setShowEdit] = useState(false);

  return (
    <Box css={{ p: "$4" }}>
      <Button onClick={goBack}>← Back</Button>
      <h2>{course.name}</h2>
      <Badge>
        {course.status === "0" ? "Draft" : "Published"}
      </Badge>
      <div>Enrolled: {course.enrolled}</div>

      <Box css={{ mt: "$3" }}>
        <Button onClick={() => setTab("details")}>Details</Button>
        <Button onClick={() => setTab("lessons")}>Lessons</Button>
        <Button onClick={() => setTab("chapters")}>Chapters</Button>
        <Button onClick={() => setTab("outline")}>Outline</Button>
        <Button onClick={() => setShowEdit(true)}>Edit</Button>
      </Box>

      {tab === "details" && (
        <Box css={{ mt: "$3" }}>
          {course.description}
        </Box>
      )}
      {tab === "lessons" && (
        <LessonsTab courseId={course.id} />
      )}
      {tab === "chapters" && (
        <ChaptersTab courseId={course.id} />
      )}
      {tab === "outline" && (
        <OutlineTab courseId={course.id} />
      )}

      {showEdit && (
        <CourseForm
          course={course}
          onClose={() => setShowEdit(false)}
        />
      )}
      <ConfirmDialog
        message="Delete this course?"
        onConfirm={() => {
          window.openai?.callTool("tc_delete_course", {
            courseId: course.id,
            orgId: course.orgId,
          });
          goBack();
        }}
      />
    </Box>
  );
}
