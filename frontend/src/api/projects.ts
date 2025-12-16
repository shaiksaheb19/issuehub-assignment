import api from "./http";

export type Project = {
  id: number;
  name: string;
  key: string;
  description: string | null;
};

export async function getProjects(): Promise<Project[]> {
  const { data } = await api.get("/api/projects/");
  return data;
}

export async function createProject(input: {
  name: string;
  key: string;
  description?: string;
}): Promise<Project> {
  const { data } = await api.post("/api/projects/", input);
  return data;
}
