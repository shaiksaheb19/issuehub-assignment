import api from "./http";

export type Comment = {
  id: number;
  issue_id: number;
  author_id: number;
  body: string;
  created_at: string;
};

export async function getComments(issueId: number): Promise<Comment[]> {
  const { data } = await api.get(`/api/issues/${issueId}/comments`);
  return data;
}

export async function createComment(
  issueId: number,
  body: string
): Promise<Comment> {
  const { data } = await api.post(`/api/issues/${issueId}/comments`, { body });
  return data;
}
