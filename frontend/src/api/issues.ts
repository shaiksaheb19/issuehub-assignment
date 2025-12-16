// frontend/src/api/issues.ts
import api from "./http";

export type IssueStatus = "open" | "in_progress" | "closed"; // match backend IssueStatusEnum
export type Priority = "low" | "medium" | "high";

export type Issue = {
  id: number;
  project_id: number;
  title: string;
  description: string | null;
  status: IssueStatus;
  priority: Priority;
  reporter_id: number;
  assignee_id: number | null;
  created_at: string;
};

export async function getIssues(projectId: number): Promise<Issue[]> {
  const { data } = await api.get(`/api/projects/${projectId}/issues`);
  return data;
}

export async function createIssue(
  projectId: number,
  input: { title: string; description?: string; priority: Priority }
): Promise<Issue> {
  const { data } = await api.post(`/api/projects/${projectId}/issues`, input);
  return data;
}

export async function updateIssueStatus(
  issueId: number,
  status: IssueStatus
): Promise<Issue> {
  const { data } = await api.patch(`/api/issues/${issueId}`, { status });
  return data;
}
