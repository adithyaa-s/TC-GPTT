import React from "react";
import { Card, CardBody, Badge, Button } from "./ui";

export default function CourseCard({ course, onClick }) {
  return (
    <Card css={{ cursor: "pointer" }}>
      <CardBody>
        <h3>{course.name}</h3>
        <Badge>{course.status === "0" ? "Draft" : "Published"}</Badge>
        <div style={{ marginTop: "8px" }}>
          Enrolled: {course.enrolled}
        </div>
        <Button onClick={onClick}>Details</Button>
      </CardBody>
    </Card>
  );
}
