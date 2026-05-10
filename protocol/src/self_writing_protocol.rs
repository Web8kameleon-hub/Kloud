use serde::{Deserialize, Serialize};

use crate::governance_contracts::{
    evaluate_governance, GovernanceDecision, GovernanceEnvelope, JonaSandboxPolicy,
};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum ProposalStage {
    Draft,
    SandboxValidated,
    ProductionEnabled,
    Rejected,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SelfWritingProposal {
    pub proposal_id: String,
    pub title: String,
    pub protocol_patch: String,
    pub governance: GovernanceEnvelope,
    pub stage: ProposalStage,
}

impl SelfWritingProposal {
    pub fn new(
        proposal_id: impl Into<String>,
        title: impl Into<String>,
        protocol_patch: impl Into<String>,
        governance: GovernanceEnvelope,
    ) -> Self {
        Self {
            proposal_id: proposal_id.into(),
            title: title.into(),
            protocol_patch: protocol_patch.into(),
            governance,
            stage: ProposalStage::Draft,
        }
    }

    pub fn review_with_policy(&mut self, policy: &JonaSandboxPolicy) -> ProposalStage {
        let audit = evaluate_governance(&self.governance, policy);
        self.stage = match audit.decision {
            GovernanceDecision::Approved => ProposalStage::ProductionEnabled,
            GovernanceDecision::SandboxOnly => ProposalStage::SandboxValidated,
            GovernanceDecision::Rejected => ProposalStage::Rejected,
        };
        self.stage.clone()
    }
}
