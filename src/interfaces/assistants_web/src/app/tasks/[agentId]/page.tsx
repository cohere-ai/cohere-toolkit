'use client';

import { useAgent, useAgentTasks } from '@/hooks/agents';

type Props = {
  params: {
    agentId: string;
  };
  searchParams: Record<string, string>;
};

const Page = ({ params }: Props) => {
  const agentId = params.agentId;
  const {
    data: agentTasks,
    isLoading: isTaskLoading,
    error: isTaskError,
  } = useAgentTasks({ agentId });
  const { data: agent, isLoading, error } = useAgent({ agentId });

  if (error || isTaskError) {
    return <div>Error: {error?.message}</div>;
  }

  if (isLoading || isTaskLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="m-12">
      <h1 className="mb-4 mt-4 text-2xl bg-slate-400 p-16">Tasks report for {agent?.name}</h1>
      <table className="table-fixed bg-slate-400 p-16 text-balance border-separate border-spacing-2 border border-slate-500 ">
        <thead className="text-xl">
          <tr>
            <th>Task ID</th>
            <th>Task Name</th>
            <th>Task Status</th>
            <th>Task Result</th>
            <th>Exception Snippet</th>
          </tr>
        </thead>
        <tbody className="text">
          {(agentTasks || []).map((task) => (
            <tr key={task.task_id}>
              <td>{task.task_id}</td>
              <td>{task.name}</td>
              <td>{task.status}</td>
              <td>{JSON.stringify(task.result, null, 2)}</td>
              <td>{task?.exception_snippet || ''}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Page;
