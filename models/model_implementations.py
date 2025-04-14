from models.openai_model import OpenAIModel

class GPT45Model(OpenAIModel):
    """Wrapper for GPT-4.5 model"""
    
    def __init__(self):
        super().__init__(model_name="gpt-4.5-preview", config_prefix="GPT45")
        self.capabilities = ["text_generation", "function_calling", "advanced_reasoning"]
        self.description = "GPT-4.5 is a large language model with advanced reasoning capabilities."
        
    def get_capabilities(self):
        return self.capabilities
        

class GPTO3MiniModel(OpenAIModel):
    """Wrapper for GPT-O3 Mini model"""
    
    def __init__(self):
        super().__init__(model_name="gpt-o3-mini", config_prefix="O3_MINI")
        self.capabilities = ["text_generation", "function_calling", "efficient_processing"]
        self.description = "GPT-O3 Mini is a compact, efficient language model for lighter workloads."
        
    def get_capabilities(self):
        return self.capabilities