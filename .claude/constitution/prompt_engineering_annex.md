# Prompt Engineering Standard

## 1. Structured Template (XML-lite)
Use for complex tasks to ensure constraint compliance.
```xml
<task_definition>
  <objective>Goal</objective>
  <context>Context</context>
</task_definition>
<reqs>
  <req id="1">Requirement</req>
</reqs>
<constraints>
  <constraint type="neg">Negative constraints</constraint>
</constraints>
<output_format>Schema/Style</output_format>
<validation>Verification steps</validation>
```

## 2. Integration & Best Practices
- **Optimization**: Offer to optimize raw prompts before execution.
- **Negative Constraints**: Explicitly state what NOT to do.
- **Chain of Thought**: Use `<thinking>` tags to plan.
- **Few-Shot**: Provide concrete examples.
