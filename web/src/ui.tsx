import React from "react";
import {
  Box,
  Button,
  Input,
  Tab,
  TabList,
  TabPanels,
  Tabs,
  Text,
  Card,
  CardBody,
  Badge,
  Spinner,
  Stack,
} from "@openai/apps-sdk-ui";

export { Box, Button, Input, Card, Badge, Spinner, Stack };

export function PageHeader({ title, children }) {
  return (
    <Box css={{ mb: "$4" }}>
      <Text as="h1" size="2xl" weight="bold">
        {title}
      </Text>
      {children}
    </Box>
  );
}
