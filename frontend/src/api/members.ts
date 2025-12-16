// frontend/src/api/members.ts
import api from "./http";

export type Role = "viewer" | "developer" | "manager"; // match RoleEnum

export type ProjectMember = {
  id: number;
  project_id: number;
  user_id: number;
  role: Role;
  joined_at: string;
};

export async function getMembers(projectId: number): Promise<ProjectMember[]> {
  const { data } = await api.get(`/api/projects/${projectId}/members`);
  return data;
}

export async function addMember(
  projectId: number,
  input: { email: string; role: Role }
): Promise<ProjectMember> {
  const { data } = await api.post(`/api/projects/${projectId}/members`, input);
  return data;
}
