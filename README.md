# CISC-3160-Project

#Task
The task was to create an interpreter for a simple programming language where programs consist of assignments involving integer-type variables. The interpreter should:
Detect Syntax Errors
Report Uninitialized Variables
Perform Assignments and Print Variable Values

#Summary
Lexer (Lexical Analyzer)
  Purpose: Tokenizes the input source code.
  Features: Recognizes identifiers, literals, operators, parentheses, assignment operators, and semicolons. Detects lexical errors like invalid numbers with leading zeros.

Parser (Syntax Analyzer)
  Purpose: Builds an Abstract Syntax Tree (AST) based on the language grammar.
  Features: Implements the grammar rules: Assignment, Exp, Term, Fact.
  Validates correct syntax and raises errors when violations occur.

Interpreter (Executor)
  Purpose: Evaluates the AST and performs assignments.
  Features: Evaluates expressions using arithmetic operators (+, -, *) and handles unary operators.
  Reports uninitialized variables and supports nested expressions.
  Prints variable values if no errors occur.
