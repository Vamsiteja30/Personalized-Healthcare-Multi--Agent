import React from 'react';
import { CopilotKit } from '@copilotkit/react-core';

interface CopilotKitProviderProps {
  children: React.ReactNode;
}

const CopilotKitProvider: React.FC<CopilotKitProviderProps> = ({ children }) => {
  return (
    <CopilotKit
      publicApiKey="demo-key"
    >
      {children}
    </CopilotKit>
  );
};

export default CopilotKitProvider;
