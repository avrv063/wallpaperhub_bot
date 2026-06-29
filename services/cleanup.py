import os

from repositories.candidates import get_cleanup_candidates, delete_candidate


async def cleanup_candidates_files() -> dict:
    candidates = await get_cleanup_candidates()

    deleted_files = 0
    deleted_rows = 0
    errors = []

    for candidate_id, file_path in candidates:
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                deleted_files += 1

            await delete_candidate(candidate_id)
            deleted_rows += 1

        except Exception as e:
            errors.append(f"{candidate_id}: {e}")

    return {
        "deleted_files": deleted_files,
        "deleted_rows": deleted_rows,
        "errors": errors,
    }