using AIAugmentedPitchAnalyzer.Application.Interfaces.IRepository;
using AIAugmentedPitchAnalyzer.Domain.Entities;
using AIAugmentedPitchAnalyzer.Persistence.Context;
using Microsoft.EntityFrameworkCore;
using System;
using System.Threading.Tasks;

namespace AIAugmentedPitchAnalyzer.Persistence.Repositories
{
    public class StartupRepository : GenericRepository<Startup>, IStartupRepository
    {
        public StartupRepository(ApplicationDbContext context) : base(context)
        {
        }

        public async Task<Startup?> GetWithPitchesAsync(Guid startupId)
        {
            return await _dbSet.AsNoTracking().Include(s => s.Pitches!).ThenInclude(p => p.Analysis).FirstOrDefaultAsync(s => s.Id == startupId);
        }

        public async Task<(IEnumerable<Startup> Items, int TotalCount)> GetPagedAsync(int pageNumber, int pageSize, Domain.Enums.Industry? industry = null, string? search = null)
        {
            var query = _dbSet.AsNoTracking().Include(s => s.Pitches!).ThenInclude(p => p.Analysis).AsQueryable();

            if (industry.HasValue)
            {
                query = query.Where(s => s.Industry == industry.Value);
            }

            if (!string.IsNullOrWhiteSpace(search))
            {
                var q = search.Trim().ToLowerInvariant();
                query = query.Where(s => (s.Name != null && s.Name.ToLower().Contains(q)) || (s.BusinessDescription != null && s.BusinessDescription.ToLower().Contains(q)) || (s.FounderName != null && s.FounderName.ToLower().Contains(q)));
            }

            var total = await query.CountAsync();
            var skip = (Math.Max(1, pageNumber) - 1) * Math.Max(1, pageSize);
            var items = await query.OrderBy(s => s.Name).Skip(skip).Take(Math.Max(1, pageSize)).ToListAsync();

            return (items, total);
        }
    }
}
