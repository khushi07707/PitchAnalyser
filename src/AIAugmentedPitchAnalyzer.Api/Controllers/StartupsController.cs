using System;
using System.Threading.Tasks;
using AIAugmentedPitchAnalyzer.Application.DTOs.Startup;
using AIAugmentedPitchAnalyzer.Application.Interfaces.IServices;
using AIAugmentedPitchAnalyzer.Shared.Responses;
using AutoMapper;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace AIAugmentedPitchAnalyzer.Api.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class StartupsController : ControllerBase
    {
        private readonly IStartupService _startupService;
        private readonly IMapper _mapper;

        public StartupsController(IStartupService startupService, IMapper mapper)
        {
            _startupService = startupService;
            _mapper = mapper;
        }

        [HttpPost]
        [Authorize]
        public async Task<IActionResult> Create([FromBody] CreateStartupRequest request)
        {
            if (request == null) return BadRequest(new ApiResponse<StartupDto> { Success = false, Message = "Invalid request" });

            // determine caller id from token if available
            Guid createdBy = Guid.Empty;
            if (User?.Identity?.IsAuthenticated == true)
            {
                var sub = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value ?? User.FindFirst("sub")?.Value;
                Guid.TryParse(sub, out createdBy);
            }

            var result = await _startupService.CreateStartupAsync(request, createdBy);
            if (!result.Success) return BadRequest(result);

            return CreatedAtAction(nameof(GetById), new { id = result.Data.Id }, result);
        }

        [HttpGet("{id}")]
        [Authorize]
        public async Task<IActionResult> GetById(Guid id)
        {
            var result = await _startupService.GetStartupAsync(id);
            if (!result.Success) return NotFound(result);
            return Ok(result);
        }

        [HttpGet]
        [Authorize]
        public async Task<IActionResult> GetAll([FromQuery] int pageNumber = 1, [FromQuery] int pageSize = 20, [FromQuery] AIAugmentedPitchAnalyzer.Domain.Enums.Industry? industry = null, [FromQuery] string? search = null)
        {
            var result = await _startupService.GetAllAsync(pageNumber, pageSize, industry, search);

            if (result.Success && result.Data != null)
            {
                var baseUrl = $"{Request.Scheme}://{Request.Host}{Request.Path}";

                string BuildUrl(int page)
                {
                    var q = new System.Collections.Generic.Dictionary<string, string?>();
                    q["pageNumber"] = page.ToString();
                    q["pageSize"] = pageSize.ToString();
                    if (industry.HasValue) q["industry"] = industry.Value.ToString();
                    if (!string.IsNullOrWhiteSpace(search)) q["search"] = search;
                    return Microsoft.AspNetCore.WebUtilities.QueryHelpers.AddQueryString(baseUrl, q as System.Collections.Generic.IDictionary<string, string?>);
                }

                if (result.Data.TotalPages > 0)
                {
                    result.Data.FirstPageUrl = BuildUrl(1);
                    result.Data.LastPageUrl = BuildUrl(result.Data.TotalPages);
                }

                if (result.Data.PageNumber < result.Data.TotalPages)
                {
                    result.Data.NextPageUrl = BuildUrl(result.Data.PageNumber + 1);
                }

                if (result.Data.PageNumber > 1)
                {
                    result.Data.PrevPageUrl = BuildUrl(result.Data.PageNumber - 1);
                }
            }

            return Ok(result);
        }

        [HttpPut("{id}")]
        [Authorize(Roles = "Founder,Admin")]
        public async Task<IActionResult> Update(Guid id, [FromBody] UpdateStartupRequest request)
        {
            if (request == null) return BadRequest(new ApiResponse<StartupDto> { Success = false, Message = "Invalid request" });

            Guid updatedBy = Guid.Empty;
            if (User?.Identity?.IsAuthenticated == true)
            {
                var sub = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value ?? User.FindFirst("sub")?.Value;
                Guid.TryParse(sub, out updatedBy);
            }

            var result = await _startupService.UpdateStartupAsync(id, request, updatedBy);
            if (!result.Success) return BadRequest(result);
            return Ok(result);
        }

        [HttpDelete("{id}")]
        [Authorize(Roles = "Founder,Admin")]
        public async Task<IActionResult> Delete(Guid id)
        {
            Guid deletedBy = Guid.Empty;
            if (User?.Identity?.IsAuthenticated == true)
            {
                var sub = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value ?? User.FindFirst("sub")?.Value;
                Guid.TryParse(sub, out deletedBy);
            }

            var result = await _startupService.DeleteStartupAsync(id, deletedBy);
            if (!result.Success) return BadRequest(result);
            return NoContent();
        }
    }
}
