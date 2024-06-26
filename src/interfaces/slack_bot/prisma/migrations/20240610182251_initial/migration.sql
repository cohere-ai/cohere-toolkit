-- CreateTable
CREATE TABLE "OAuthInstallation" (
    "id" SERIAL NOT NULL,
    "teamId" TEXT,
    "enterpriseId" TEXT,
    "installation" JSONB NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "OAuthInstallation_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "WorkspaceSettings" (
    "id" SERIAL NOT NULL,
    "teamId" TEXT,
    "enterpriseId" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "WorkspaceSettings_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ChannelSettings" (
    "id" SERIAL NOT NULL,
    "channelId" TEXT NOT NULL,
    "workspaceId" INTEGER NOT NULL,
    "modelName" TEXT,
    "temperature" DOUBLE PRECISION,
    "preamble" TEXT,
    "tools" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "ChannelSettings_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "OAuthInstallation_teamId_key" ON "OAuthInstallation"("teamId");

-- CreateIndex
CREATE UNIQUE INDEX "OAuthInstallation_enterpriseId_key" ON "OAuthInstallation"("enterpriseId");

-- CreateIndex
CREATE INDEX "OAuthInstallation_teamId_idx" ON "OAuthInstallation"("teamId");

-- CreateIndex
CREATE INDEX "OAuthInstallation_enterpriseId_idx" ON "OAuthInstallation"("enterpriseId");

-- CreateIndex
CREATE UNIQUE INDEX "WorkspaceSettings_teamId_key" ON "WorkspaceSettings"("teamId");

-- CreateIndex
CREATE UNIQUE INDEX "WorkspaceSettings_enterpriseId_key" ON "WorkspaceSettings"("enterpriseId");

-- CreateIndex
CREATE INDEX "WorkspaceSettings_teamId_idx" ON "WorkspaceSettings"("teamId");

-- CreateIndex
CREATE INDEX "WorkspaceSettings_enterpriseId_idx" ON "WorkspaceSettings"("enterpriseId");

-- CreateIndex
CREATE INDEX "ChannelSettings_channelId_workspaceId_idx" ON "ChannelSettings"("channelId", "workspaceId");

-- CreateIndex
CREATE UNIQUE INDEX "ChannelSettings_channelId_workspaceId_key" ON "ChannelSettings"("channelId", "workspaceId");

-- AddForeignKey
ALTER TABLE "ChannelSettings" ADD CONSTRAINT "ChannelSettings_workspaceId_fkey" FOREIGN KEY ("workspaceId") REFERENCES "WorkspaceSettings"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
