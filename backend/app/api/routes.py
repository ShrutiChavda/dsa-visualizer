"""
DSA Visualizer - API Routes
"""
from fastapi import APIRouter, HTTPException
from app.core.ast_engine import ASTEngine
from app.models.events import ExecuteRequest, ExecutionResult, DSAProblem
from app.services.problems import get_problem, list_problems

router = APIRouter()


@router.post("/execute", response_model=ExecutionResult)
def execute_code(request: ExecuteRequest):
    """
    Execute Python code and return step-by-step execution events.
    """
    # Safety: limit code length
    if len(request.code) > 5000:
        raise HTTPException(400, "Code too long (max 5000 chars)")

    engine = ASTEngine()
    result = engine.execute(request.code, request.initial_vars)
    return result


@router.get("/problems")
def get_problems():
    """List all available DSA problems."""
    return {"problems": list_problems()}


@router.get("/problems/{problem_id}", response_model=DSAProblem)
def get_problem_by_id(problem_id: str):
    """Get a specific DSA problem by ID."""
    problem = get_problem(problem_id)
    if not problem:
        raise HTTPException(404, f"Problem '{problem_id}' not found")
    return problem


@router.post("/problems/{problem_id}/execute", response_model=ExecutionResult)
def execute_problem(problem_id: str):
    """Execute a built-in DSA problem."""
    problem = get_problem(problem_id)
    if not problem:
        raise HTTPException(404, f"Problem '{problem_id}' not found")

    engine = ASTEngine()
    result = engine.execute(problem.code, problem.initial_vars)
    return result
