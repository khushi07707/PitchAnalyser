using System;
using System.Security.Claims;
using System.Threading.Tasks;
using AIAugmentedPitchAnalyzer.Application.Interfaces.IServices;
using AIAugmentedPitchAnalyzer.Shared.Responses;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace AIAugmentedPitchAnalyzer.Api.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class PitchAnalysisController : ControllerBase
    {
        private readonly IPitchAnalysisService _pitchAnalysisService;

        public PitchAnalysisController(IPitchAnalysisService pitchAnalysisService)
        {
            _pitchAnalysisService = pitchAnalysisService;
        }

        [HttpPost("{pitchId}/analyze")]
        [Authorize]
        public async Task<IActionResult> AnalyzePitch(Guid pitchId)
        {
            var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value ?? User.FindFirst("sub")?.Value;
            if (!Guid.TryParse(userIdClaim, out var userId))
            {
                return Unauthorized(new ApiResponse<object> { Success = false, Message = "Invalid or missing user identity." });
            }

            var result = await _pitchAnalysisService.AnalyzePitchAsync(pitchId, userId);
            if (!result.Success)
            {
                return BadRequest(result);
            }

            return Ok(result);
        }

        [HttpGet("{pitchId}")]
        [Authorize]
        public async Task<IActionResult> GetPitchAnalysis(Guid pitchId)
        {
            var result = await _pitchAnalysisService.GetPitchAnalysisAsync(pitchId);
            if (!result.Success)
            {
                return NotFound(result);
            }

            return Ok(result);
        }

        /// <summary>
        /// Retrieves the parsed AI analysis for a pitch, including summary, score, and recommendations.
        /// </summary>
        /// <param name="pitchId">The pitch identifier.</param>
        /// <returns>A parsed pitch analysis result.</returns>
        [HttpGet("{pitchId}/parsed")]
        [ProducesResponseType(typeof(ApiResponse<object>), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(ApiResponse<object>), StatusCodes.Status404NotFound)]
        [Authorize]
        public async Task<IActionResult> GetParsedPitchAnalysis(Guid pitchId)
        {
            var result = await _pitchAnalysisService.GetParsedPitchAnalysisAsync(pitchId);
            if (!result.Success)
            {
                return NotFound(result);
            }

            return Ok(result);
        }

        [HttpGet("dashboard")]
        [Authorize]
        public async Task<IActionResult> GetDashboard()
        {
            var result = await _pitchAnalysisService.GetDashboardAsync();
            return Ok(result);
        }

        [HttpGet("history")]
        [Authorize]
        public async Task<IActionResult> GetAnalysisHistory()
        {
            var result = await _pitchAnalysisService.GetAnalysisHistoryAsync();
            return Ok(result);
        }
    }
}
