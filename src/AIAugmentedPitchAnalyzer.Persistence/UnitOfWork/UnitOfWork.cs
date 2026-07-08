using AIAugmentedPitchAnalyzer.Application.Interfaces.IUnitOfWork;
using AIAugmentedPitchAnalyzer.Persistence.Context;
using System.Threading.Tasks;

namespace AIAugmentedPitchAnalyzer.Persistence.UnitOfWork
{
    public class UnitOfWork : IUnitOfWork
    {
        private readonly ApplicationDbContext _context;

        public UnitOfWork(ApplicationDbContext context)
        {
            _context = context;
        }

        public async Task<int> SaveChangesAsync()
        {
            return await _context.SaveChangesAsync();
        }
    }
}
