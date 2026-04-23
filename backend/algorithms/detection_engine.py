from algorithms.rag_builder import RAGBuilder
from algorithms.cycle_detection import CycleDetection
from algorithms.bankers_algorithm import BankersAlgorithm
from utils.logger import Logger
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
import os


class DetectionEngine:
    def __init__(self, system_state):
        self.system_state = system_state
        self.logger = Logger()

    def detect_deadlock(self):
        self.logger.log("Starting deadlock detection")

        rag_builder = RAGBuilder(self.system_state)
        graph = rag_builder.build_graph()

        self.logger.log(
            f"Built RAG with {graph.number_of_nodes()} nodes "
            f"and {graph.number_of_edges()} edges"
        )

        cycle_detector = CycleDetection(graph)
        cycle_result = cycle_detector.detect()

        self.logger.log(f"Cycle detection result: {cycle_result['has_deadlock']}")

        bankers = BankersAlgorithm(self.system_state)
        bankers_result = bankers.detect_deadlock()

        self.logger.log(f"Banker's algorithm result: {bankers_result['has_deadlock']}")

        # ── Consistency rule ──────────────────────────────────────────────
        # If a cycle is detected the system MUST be considered unsafe.
        # Override Banker's result to stay consistent.
        if cycle_result['has_deadlock'] and bankers_result['is_safe']:
            bankers_result['is_safe']       = False
            bankers_result['has_deadlock']  = True
            bankers_result['state']         = 'unsafe'
            bankers_result['safe_sequence'] = None
            self.logger.log(
                "Cycle detected – overriding Banker's safe result to unsafe "
                "for consistency."
            )

        has_deadlock = cycle_result['has_deadlock'] or bankers_result['has_deadlock']

        involved_processes = list(set(
            cycle_result.get('involved_processes', []) +
            bankers_result.get('unsafe_processes', [])
        ))

        result = {
            'deadlock':           has_deadlock,
            'involved_processes': involved_processes,
            'cycle_detection':    cycle_result,
            'bankers_algorithm':  bankers_result,
            'graph_info': {
                'nodes': graph.number_of_nodes(),
                'edges': graph.number_of_edges(),
            },
        }

        self.logger.log(f"Final detection result: deadlock={has_deadlock}")

        return result, graph

    def visualize_graph(self, graph, output_path=None):
        if output_path is None:
            _here = os.path.dirname(os.path.abspath(__file__))
            output_path = os.path.normpath(os.path.join(_here, '..', 'static', 'graph.png'))
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        fig, ax = plt.subplots(figsize=(13, 8))
        ax.set_facecolor('#f8fafc')
        fig.patch.set_facecolor('#f8fafc')

        if graph.number_of_nodes() == 0:
            ax.text(0.5, 0.5, 'No nodes to display', ha='center', va='center',
                    transform=ax.transAxes, fontsize=14, color='#94a3b8')
            plt.axis('off')
            plt.tight_layout()
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            return output_path

        pos = nx.spring_layout(graph, k=2.5, iterations=80, seed=42)

        process_nodes  = [n for n, d in graph.nodes(data=True) if d.get('node_type') == 'process']
        resource_nodes = [n for n, d in graph.nodes(data=True) if d.get('node_type') == 'resource']
        request_edges    = [(u, v) for u, v, d in graph.edges(data=True) if d.get('edge_type') == 'request']
        allocation_edges = [(u, v) for u, v, d in graph.edges(data=True) if d.get('edge_type') == 'allocation']

        # Draw process nodes (circles)
        nx.draw_networkx_nodes(graph, pos, ax=ax, nodelist=process_nodes,
                               node_color='#93c5fd', node_shape='o',
                               node_size=2200, edgecolors='#2563eb', linewidths=2)

        # Draw resource nodes (squares)
        nx.draw_networkx_nodes(graph, pos, ax=ax, nodelist=resource_nodes,
                               node_color='#86efac', node_shape='s',
                               node_size=2200, edgecolors='#16a34a', linewidths=2)

        # Request edges – dashed red
        if request_edges:
            nx.draw_networkx_edges(graph, pos, ax=ax, edgelist=request_edges,
                                   edge_color='#dc2626', style='dashed',
                                   arrows=True, arrowsize=22, width=2,
                                   connectionstyle='arc3,rad=0.08',
                                   min_source_margin=28, min_target_margin=28)

        # Allocation edges – solid blue
        if allocation_edges:
            nx.draw_networkx_edges(graph, pos, ax=ax, edgelist=allocation_edges,
                                   edge_color='#2563eb', style='solid',
                                   arrows=True, arrowsize=22, width=2,
                                   connectionstyle='arc3,rad=0.08',
                                   min_source_margin=28, min_target_margin=28)

        nx.draw_networkx_labels(graph, pos, ax=ax, font_size=10,
                                font_weight='bold', font_color='#0f172a')

        # Legend
        from matplotlib.lines import Line2D
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#93c5fd', edgecolor='#2563eb', label='Process (circle)'),
            Patch(facecolor='#86efac', edgecolor='#16a34a', label='Resource (square)'),
            Line2D([0], [0], color='#dc2626', linewidth=2, linestyle='dashed', label='Request edge'),
            Line2D([0], [0], color='#2563eb', linewidth=2, linestyle='solid',  label='Allocation edge'),
        ]
        ax.legend(handles=legend_elements, loc='upper left', framealpha=0.9,
                  fontsize=9, edgecolor='#e2e8f0')

        ax.set_title('Resource Allocation Graph (RAG)', fontsize=15,
                     fontweight='bold', color='#0f172a', pad=14)
        ax.axis('off')
        plt.tight_layout()

        plt.savefig(output_path, dpi=150, bbox_inches='tight',
                    facecolor=fig.get_facecolor())
        plt.close()

        self.logger.log(f"Graph visualization saved to {output_path}")
        return output_path
